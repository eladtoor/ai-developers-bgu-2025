import chromadb

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# List all collections
print("📊 Available ChromaDB Collections:")
collections = client.list_collections()
for collection in collections:
    print(f"- {collection.name}")

if collections:
    # Use the first collection
    collection = collections[0]
    print(f"\n📄 Using collection: {collection.name}")
    print(f"Count: {collection.count()} documents")
    
    # Get a few sample documents
    print("\n📄 Sample Documents:")
    try:
        results = collection.query(
            query_texts=["What time did Sarah call 911?"],
            n_results=3
        )
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n--- Document {i+1} ---")
            print(f"Text: {doc}")
            print(f"Metadata: {metadata}")
    except Exception as e:
        print(f"Error querying: {e}")
else:
    print("❌ No collections found!")

print("\n✅ Data check complete!") 