"""
Jarvis RPG Engine v3.0 - The Ultimate AI Text Adventure
Features: Turn-based Combat, Inventory System, Loot, Leveling, and AI Narration.
"""

import streamlit as st
import random
from datetime import datetime

# ==========================================
# GAME DATABASE
# ==========================================
CHARACTER_CLASSES = {
    "⚔️ Warrior": {
        "desc": "High HP & Strength. Master of melee combat.",
        "stats": {"hp": 150, "max_hp": 150, "mp": 30, "max_mp": 30, "str": 18, "int": 8, "agi": 10, "luck": 10},
        "items": ["Iron Sword", "Health Potion x3"],
        "ability": "Power Strike (2x Damage)"
    },
    "🧙 Mage": {
        "desc": "High Intelligence & Magic. Devastating spells.",
        "stats": {"hp": 90, "max_hp": 90, "mp": 100, "max_mp": 100, "str": 6, "int": 22, "agi": 12, "luck": 12},
        "items": ["Magic Staff", "Mana Potion x3"],
        "ability": "Fireball (High Magic Dmg)"
    },
    "🗡️ Rogue": {
        "desc": "High Agility & Luck. Critical hits & evasion.",
        "stats": {"hp": 110, "max_hp": 110, "mp": 50, "max_mp": 50, "str": 12, "int": 14, "agi": 22, "luck": 20},
        "items": ["Twin Daggers", "Smoke Bomb x2"],
        "ability": "Backstab (Crit Chance)"
    },
    "🏹 Ranger": {
        "desc": "Balanced stats. Ranged attacks & survival.",
        "stats": {"hp": 120, "max_hp": 120, "mp": 60, "max_mp": 60, "str": 14, "int": 12, "agi": 18, "luck": 15},
        "items": ["Longbow", "Herb Bundle x3"],
        "ability": "Multi-Shot (Hit all)"
    }
}

MONSTERS = [
    {"name": "🐺 Wild Wolf", "hp": 40, "atk": 8, "def": 2, "xp": 20, "gold": 10},
    {"name": "👺 Goblin Scout", "hp": 60, "atk": 12, "def": 4, "xp": 35, "gold": 25},
    {"name": "🧟 Zombie Knight", "hp": 90, "atk": 15, "def": 8, "xp": 60, "gold": 40},
    {"name": "🐉 Young Dragon", "hp": 150, "atk": 25, "def": 12, "xp": 150, "gold": 100},
    {"name": "👻 Phantom", "hp": 70, "atk": 20, "def": 5, "xp": 80, "gold": 50}
]

LOOT_TABLE = [
    {"name": "Health Potion", "type": "consumable", "effect": "heal", "value": 50},
    {"name": "Mana Potion", "type": "consumable", "effect": "mana", "value": 30},
    {"name": "Gold Coins", "type": "currency", "value": 25},
    {"name": "Magic Scroll", "type": "consumable", "effect": "magic_dmg", "value": 40}
]

# ==========================================
# STATE MANAGEMENT
# ==========================================
def init_rpg():
    if "rpg" not in st.session_state:
        st.session_state.rpg = {
            "state": "MENU",  # MENU, PLAYING, COMBAT, GAME_OVER
            "player": None,
            "enemy": None,
            "log": [],
            "turn": 0
        }

def reset_rpg():
    st.session_state.rpg = {
        "state": "MENU",
        "player": None,
        "enemy": None,
        "log": [],
        "turn": 0
    }

# ==========================================
# AI NARRATOR (Groq)
# ==========================================
def ai_narrate(prompt, system="You are a dramatic fantasy storyteller. Be vivid and concise (max 3 sentences)."):
    try:
        from groq import Groq
        from config import Config
        if not Config.GROQ_API_KEY: return "..."
        client = Groq(api_key=Config.GROQ_API_KEY)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.8, max_tokens=150
        )
        return resp.choices[0].message.content
    except: return "..."

# ==========================================
# GAME LOGIC
# ==========================================
def create_player(name, cls_name):
    cls = CHARACTER_CLASSES[cls_name]
    st.session_state.rpg["player"] = {
        "name": name, "class": cls_name, "level": 1, "xp": 0, "gold": 50,
        "stats": cls["stats"].copy(), "items": cls["items"].copy(),
        "ability": cls["ability"]
    }
    st.session_state.rpg["state"] = "PLAYING"
    add_log(f"✨ {name} the {cls_name} enters the realm!")

def add_log(msg):
    st.session_state.rpg["log"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}")
    if len(st.session_state.rpg["log"]) > 50: st.session_state.rpg["log"].pop(0)

def explore():
    p = st.session_state.rpg["player"]
    roll = random.random()
    
    if roll < 0.6:  # 60% Combat
        enemy = random.choice(MONSTERS)
        # Scale enemy to player level
        enemy["hp"] = int(enemy["hp"] * (1 + p["level"]*0.2))
        enemy["atk"] = int(enemy["atk"] * (1 + p["level"]*0.1))
        st.session_state.rpg["enemy"] = enemy.copy()
        st.session_state.rpg["state"] = "COMBAT"
        add_log(f"⚔️ A wild {enemy['name']} appears!")
    elif roll < 0.8:  # 20% Loot
        item = random.choice(LOOT_TABLE)
        if item["type"] == "currency":
            p["gold"] += item["value"]
            add_log(f"💰 Found {item['value']} Gold!")
        else:
            p["items"].append(item["name"])
            add_log(f"🎁 Found {item['name']}!")
        add_log(ai_narrate(f"Player found {item['name']} in a chest. Describe it dramatically."))
    else:  # 20% Story/Trap
        if random.random() > 0.5:
            dmg = random.randint(5, 15)
            p["stats"]["hp"] -= dmg
            add_log(f"🪤 Triggered a trap! Lost {dmg} HP.")
        else:
            heal = random.randint(10, 30)
            p["stats"]["hp"] = min(p["stats"]["max_hp"], p["stats"]["hp"] + heal)
            add_log(f"🌿 Found a healing spring! Restored {heal} HP.")
        
    check_game_over()

def combat_action(action):
    p = st.session_state.rpg["player"]
    e = st.session_state.rpg["enemy"]
    
    if action == "attack":
        dmg = max(1, p["stats"]["str"] + random.randint(-2, 5) - e["def"])
        # Crit chance for Rogue
        if p["class"] == "🗡️ Rogue" and random.random() < 0.3:
            dmg = int(dmg * 2)
            add_log(f"💥 CRITICAL HIT! You deal {dmg} damage to {e['name']}!")
        else:
            add_log(f"⚔️ You attack {e['name']} for {dmg} damage.")
        e["hp"] -= dmg
        
    elif action == "magic":
        if p["stats"]["mp"] >= 10:
            dmg = max(1, p["stats"]["int"] * 2 + random.randint(0, 10))
            p["stats"]["mp"] -= 10
            add_log(f"🔥 You cast a spell on {e['name']} for {dmg} magic damage!")
            e["hp"] -= dmg
        else:
            add_log("❌ Not enough Mana!")
            return
            
    elif action == "heal":
        if "Health Potion" in p["items"]:
            p["items"].remove("Health Potion")
            heal = 50
            p["stats"]["hp"] = min(p["stats"]["max_hp"], p["stats"]["hp"] + heal)
            add_log(f"🧪 Used Health Potion! Restored {heal} HP.")
        else:
            add_log("❌ No Health Potions!")
            return

    elif action == "flee":
        if random.random() < 0.5 + (p["stats"]["agi"] / 100):
            add_log(f"🏃 You successfully fled from {e['name']}!")
            st.session_state.rpg["state"] = "PLAYING"
            st.session_state.rpg["enemy"] = None
            return
        else:
            add_log(f"🚫 Failed to flee!")

    # Enemy Turn
    if e["hp"] > 0:
        e_dmg = max(1, e["atk"] + random.randint(-2, 3) - (p["stats"]["agi"] // 5))
        # Dodge chance
        if random.random() < p["stats"]["agi"] / 100:
            add_log(f"💨 You dodged {e['name']}'s attack!")
        else:
            p["stats"]["hp"] -= e_dmg
            add_log(f"🩸 {e['name']} attacks you for {e_dmg} damage!")
    else:
        # Victory
        add_log(f"🏆 You defeated {e['name']}! +{e['xp']} XP, +{e['gold']} Gold.")
        p["xp"] += e["xp"]
        p["gold"] += e["gold"]
        p["items"].append("Loot Box")
        st.session_state.rpg["enemy"] = None
        st.session_state.rpg["state"] = "PLAYING"
        check_level_up()
        
    check_game_over()

def check_level_up():
    p = st.session_state.rpg["player"]
    xp_needed = p["level"] * 100
    if p["xp"] >= xp_needed:
        p["level"] += 1
        p["xp"] -= xp_needed
        p["stats"]["max_hp"] += 20
        p["stats"]["hp"] = p["stats"]["max_hp"]
        p["stats"]["str"] += 2
        p["stats"]["int"] += 2
        add_log(f"🎉 LEVEL UP! You are now Level {p['level']}! HP fully restored.")

def check_game_over():
    if st.session_state.rpg["player"]["stats"]["hp"] <= 0:
        st.session_state.rpg["state"] = "GAME_OVER"
        add_log("💀 You have been defeated...")

# ==========================================
# UI RENDERING
# ==========================================
def render_rpg():
    init_rpg()
    rpg = st.session_state.rpg
    
    st.markdown("<h2 style='color:#FFD700;text-align:center;'>🐉 JARVIS RPG: REALM OF SHADOWS</h2>", unsafe_allow_html=True)
    
    if st.button("← Back to Tools", key="back_rpg"):
        st.session_state.selected_tool = "💬 Normal Chat"
        st.rerun()
    
    st.divider()
    
    if rpg["state"] == "MENU":
        render_menu()
    elif rpg["state"] == "PLAYING":
        render_gameplay()
    elif rpg["state"] == "COMBAT":
        render_combat()
    elif rpg["state"] == "GAME_OVER":
        render_game_over()

def render_menu():
    st.markdown("### 🎭 Character Creation")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Hero Name:", placeholder="Enter name...", key="rpg_name")
    with col2:
        cls = st.selectbox("Choose Class:", list(CHARACTER_CLASSES.keys()), key="rpg_cls")
    
    if cls:
        c = CHARACTER_CLASSES[cls]
        st.info(f"**{cls}**\n{c['desc']}\n\n**Ability:** {c['ability']}\n\n**Starting Items:** {', '.join(c['items'])}")
    
    if st.button("⚔️ BEGIN ADVENTURE", type="primary", use_container_width=True):
        if name:
            create_player(name, cls)
            st.rerun()
        else:
            st.warning("Please enter a name!")

def render_gameplay():
    p = st.session_state.rpg["player"]
    
    # Stats Panel
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"### {p['class']} {p['name']}")
        st.markdown(f"**Level:** {p['level']} | **XP:** {p['xp']}/{p['level']*100}")
        st.markdown(f"**Gold:** 💰 {p['gold']}")
        
        hp_pct = p["stats"]["hp"] / p["stats"]["max_hp"]
        st.markdown(f"**HP:** {p['stats']['hp']}/{p['stats']['max_hp']}")
        st.progress(hp_pct)
        
        mp_pct = p["stats"]["mp"] / p["stats"]["max_mp"]
        st.markdown(f"**MP:** {p['stats']['mp']}/{p['stats']['max_mp']}")
        st.progress(mp_pct)
        
        st.markdown("**🎒 Inventory:**")
        for item in set(p["items"]):
            count = p["items"].count(item)
            st.markdown(f"- {item} x{count}")
            
    with col2:
        st.markdown("### 📜 Adventure Log")
        log_container = st.container(height=300)
        with log_container:
            for msg in reversed(st.session_state.rpg["log"][-15:]):
                st.markdown(msg)
        
        st.divider()
        st.markdown("### 🧭 Actions")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🌲 Explore", use_container_width=True, type="primary"):
                explore()
                st.rerun()
        with c2:
            if st.button("🏕️ Rest (Heal)", use_container_width=True):
                p["stats"]["hp"] = min(p["stats"]["max_hp"], p["stats"]["hp"] + 20)
                p["stats"]["mp"] = min(p["stats"]["max_mp"], p["stats"]["mp"] + 10)
                add_log("🏕️ You rested and recovered some HP/MP.")
                st.rerun()
        with c3:
            if st.button("🔄 Reset Game", use_container_width=True):
                reset_rpg()
                st.rerun()

def render_combat():
    p = st.session_state.rpg["player"]
    e = st.session_state.rpg["enemy"]
    
    st.markdown(f"### ⚔️ COMBAT: {p['name']} vs {e['name']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{p['name']} (HP: {p['stats']['hp']}/{p['stats']['max_hp']})**")
        st.progress(p["stats"]["hp"] / p["stats"]["max_hp"])
    with col2:
        st.markdown(f"**{e['name']} (HP: {e['hp']}/{int(MONSTERS[0]['hp'] * (1 + p['level']*0.2))})**")
        st.progress(e["hp"] / int(MONSTERS[0]['hp'] * (1 + p['level']*0.2)))
        
    st.divider()
    
    st.markdown("### 🎯 Choose Action:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⚔️ Attack", use_container_width=True, type="primary"):
            combat_action("attack")
            st.rerun()
    with c2:
        if st.button("🔥 Magic (10 MP)", use_container_width=True):
            combat_action("magic")
            st.rerun()
    with c3:
        if st.button("🧪 Heal Potion", use_container_width=True):
            combat_action("heal")
            st.rerun()
    with c4:
        if st.button("🏃 Flee", use_container_width=True):
            combat_action("flee")
            st.rerun()
            
    st.divider()
    st.markdown("### 📜 Combat Log")
    for msg in reversed(st.session_state.rpg["log"][-10:]):
        st.markdown(msg)

def render_game_over():
    p = st.session_state.rpg["player"]
    st.error(f"💀 GAME OVER! {p['name']} has fallen.")
    st.markdown(f"**Final Stats:** Level {p['level']} | Gold {p['gold']} | XP {p['xp']}")
    
    if st.button("🔄 Try Again", type="primary", use_container_width=True):
        reset_rpg()
        st.rerun()

def render_rpg_tool():
    render_rpg()
    return "feature_rendered"