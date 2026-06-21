import chromadb
from chromadb.config import Settings
import os

class ButlerMemory:
    def __init__(self):
        self.db_path = os.path.join(os.getcwd(), "memory_db")
        os.makedirs(self.db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="jarvis_memory")
    
    def save_interaction(self, user_msg: str, ai_response: str):
        try:
            id = f"msg_{self.collection.count()}"
            self.collection.add(
                documents=[f"User: {user_msg}\nAI: {ai_response}"],
                metadatas=[{"type": "interaction"}],
                ids=[id]
            )
        except Exception as e:
            print(f"Memory save error: {e}")
    
    def get_relevant_memories(self, query: str, n_results: int = 3) -> list:
        try:
            if self.collection.count() == 0:
                return []
            results = self.collection.query(query_texts=[query], n_results=min(n_results, self.collection.count()))
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Memory query error: {e}")
            return []
    
    def clear_memory(self):
        try:
            ids = self.collection.get()['ids']
            if ids:
                self.collection.delete(ids=ids)
        except Exception as e:
            print(f"Memory clear error: {e}")