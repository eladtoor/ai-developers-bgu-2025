import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

def reset_chromadb():
    """Delete the existing ChromaDB collection to recreate with new embeddings"""
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "cybersecurity-story"
    
    try:
        # Delete the existing collection
        chroma_client.delete_collection(name=collection_name)
        print(f"✅ Deleted existing collection: {collection_name}")
        
        # Verify it's gone
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print("❌ Collection still exists!")
        except:
            print("✅ Collection successfully deleted")
            
    except Exception as e:
        print(f"❌ Error deleting collection: {e}")

if __name__ == "__main__":
    reset_chromadb() 