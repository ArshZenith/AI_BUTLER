import os
import json
from datetime import datetime

class ButlerMemory:
    """Hybrid Memory System: Vector Search + Keyword Fallback"""
    
    def __init__(self):
        self.use_chromadb = False
        self.json_memories = []
        self.json_file = "memory_fallback.json"
        
        # Try to initialize ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.db_path = os.path.join(os.getcwd(), "memory_db")
            os.makedirs(self.db_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name="jarvis_memory",
                metadata={"hnsw:space": "cosine"}
            )
            self.use_chromadb = True
            print("✅ ChromaDB memory initialized")
            
        except Exception as e:
            print(f"⚠️ ChromaDB failed ({e}), using JSON fallback memory")
            self._load_json_memory()
    
    def _load_json_memory(self):
        """Load memories from JSON file"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.json_memories = json.load(f)
            except:
                self.json_memories = []
    
    def _save_json_memory(self):
        """Save memories to JSON file"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_memories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON memory: {e}")
    
    def save_interaction(self, user_msg: str, ai_response: str):
        """Save interaction to memory"""
        timestamp = datetime.now().isoformat()
        
        if self.use_chromadb:
            try:
                doc_id = f"msg_{timestamp}_{hash(user_msg) % 10000}"
                self.collection.add(
                    documents=[f"User: {user_msg}\nAI: {ai_response}"],
                    metadatas=[{
                        "type": "interaction", 
                        "timestamp": timestamp,
                        "user_len": len(user_msg)
                    }],
                    ids=[doc_id]
                )
                
                # Auto-cleanup if too many memories (keep last 500)
                count = self.collection.count()
                if count > 500:
                    all_ids = self.collection.get(limit=count-500)['ids']
                    if all_ids:
                        self.collection.delete(ids=all_ids)
                        
            except Exception as e:
                print(f"ChromaDB save error: {e}")
                # Fallback to JSON
                self._save_to_json(user_msg, ai_response, timestamp)
        else:
            self._save_to_json(user_msg, ai_response, timestamp)
    
    def _save_to_json(self, user_msg: str, ai_response: str, timestamp: str):
        """Save to JSON fallback"""
        self.json_memories.append({
            "user": user_msg[:200],  # Truncate long messages
            "ai": ai_response[:200],
            "timestamp": timestamp
        })
        
        # Keep only last 50 memories
        if len(self.json_memories) > 50:
            self.json_memories = self.json_memories[-50:]
            
        self._save_json_memory()
    
    def get_relevant_memories(self, query: str, n_results: int = 3) -> list:
        """Get relevant memories based on query"""
        if self.use_chromadb:
            try:
                if self.collection.count() == 0:
                    return []
                    
                results = self.collection.query(
                    query_texts=[query], 
                    n_results=min(n_results, self.collection.count())
                )
                
                if results and results['documents']:
                    return results['documents'][0]
                return []
                
            except Exception as e:
                print(f"ChromaDB query error: {e}")
                # Fallback to keyword search
                return self._keyword_search(query, n_results)
        else:
            return self._keyword_search(query, n_results)
    
    def _keyword_search(self, query: str, n_results: int) -> list:
        """Simple keyword-based memory retrieval"""
        query_words = set(query.lower().split())
        relevant = []
        
        # Check last 20 memories for relevance
        for mem in reversed(self.json_memories[-20:]):
            mem_text = f"{mem['user']} {mem['ai']}".lower()
            mem_words = set(mem_text.split())
            
            # Calculate overlap
            overlap = len(query_words.intersection(mem_words))
            if overlap >= 2:  # At least 2 common words
                relevant.append(f"Previous context: {mem['user'][:100]}...")
                
            if len(relevant) >= n_results:
                break
                
        return relevant
    
    def clear_memory(self):
        """Clear all memories"""
        if self.use_chromadb:
            try:
                ids = self.collection.get()['ids']
                if ids:
                    self.collection.delete(ids=ids)
                print("✅ ChromaDB memory cleared")
            except Exception as e:
                print(f"ChromaDB clear error: {e}")
        else:
            self.json_memories = []
            self._save_json_memory()
            print("✅ JSON memory cleared")
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        if self.use_chromadb:
            try:
                return {
                    "type": "ChromaDB",
                    "count": self.collection.count(),
                    "status": "active"
                }
            except:
                pass
        
        return {
            "type": "JSON Fallback",
            "count": len(self.json_memories),
            "status": "active"
        }