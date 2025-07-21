import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import chromadb

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def list_all_chunks():
    """List all chunks in the ChromaDB collection"""
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="../utils/chroma_db")
    collection_name = "cybersecurity-story"
    
    try:
        # Get the collection
        collection = chroma_client.get_collection(name=collection_name)
        
        # Get all documents
        results = collection.get()
        
        print(f"📊 Total chunks in collection: {len(results['ids'])}")
        print("=" * 80)
        
        # List each chunk
        for i, (chunk_id, document) in enumerate(zip(results['ids'], results['documents'])):
            print(f"\n🔍 Chunk {i+1}: {chunk_id}")
            print(f"📏 Length: {len(document)} characters")
            print(f"📄 Content:")
            print("-" * 40)
            print(document)
            print("=" * 80)
            
            # Check if this chunk contains "4:55 PM"
            if "4:55 PM" in document:
                print(f"🎯 FOUND '4:55 PM' in chunk {i+1}!")
                print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error accessing ChromaDB collection: {e}")

if __name__ == "__main__":
    list_all_chunks() 