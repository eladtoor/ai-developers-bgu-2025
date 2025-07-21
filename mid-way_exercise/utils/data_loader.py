import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
import re

load_dotenv()

class StoryDataLoader:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "cybersecurity-story"
        
    def parse_story_file(self, file_path):
        """Parse story file and extract the full text"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    def create_chunks(self, story_text, chunk_size=1000, overlap=200):
        """Create overlapping chunks from story text"""
        chunks = []
        
        # Clean up the text
        story_text = re.sub(r'\s+', ' ', story_text).strip()
        
        # Split into sentences for better chunking
        sentences = re.split(r'[.!?]+', story_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append({
                    'id': f"story_chunk_{chunk_id}",
                    'text': current_chunk.strip(),
                    'metadata': {
                        'type': 'story_chunk',
                        'chunk_id': chunk_id,
                        'length': len(current_chunk)
                    }
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                words = current_chunk.split()
                if len(words) > overlap // 10:  # Rough word count for overlap
                    overlap_words = words[-(overlap // 10):]
                    current_chunk = " ".join(overlap_words) + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append({
                'id': f"story_chunk_{chunk_id}",
                'text': current_chunk.strip(),
                'metadata': {
                    'type': 'story_chunk',
                    'chunk_id': chunk_id,
                    'length': len(current_chunk)
                }
            })
        
        return chunks
    
    def get_embeddings(self, texts):
        """Get embeddings for texts using OpenAI"""
        embeddings = []
        
        for text in texts:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        
        return embeddings
    
    def setup_chroma(self):
        """Initialize Chroma collection"""
        try:
            # Try to get existing collection
            collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"Using existing Chroma collection: {self.collection_name}")
        except:
            # Create new collection if it doesn't exist
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Cybersecurity story text data"}
            )
            print(f"Created Chroma collection: {self.collection_name}")
        
        return collection
    
    def upload_to_chroma(self, chunks):
        """Upload chunks to Chroma"""
        collection = self.setup_chroma()
        
        # Get embeddings for all chunks
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.get_embeddings(texts)
        
        # Prepare data for Chroma
        ids = [chunk['id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Add to Chroma collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Uploaded {len(chunks)} story chunks to Chroma")
        return collection

def main():
    """Main function to load and upload story data"""
    loader = StoryDataLoader()
    
    # Parse story file
    print("Parsing story file...")
    story_text = loader.parse_story_file('../data/The_Day_Everything_Slowed_Down.txt')
    print(f"Story length: {len(story_text)} characters")
    
    # Create chunks
    print("Creating chunks...")
    chunks = loader.create_chunks(story_text)
    print(f"Created {len(chunks)} chunks")
    
    # Show sample chunks
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1} (first 200 chars):")
        print(chunk['text'][:200] + "...")
    
    # Upload to Chroma
    print("\nUploading to Chroma...")
    collection = loader.upload_to_chroma(chunks)
    
    print("✅ Story data loading complete!")

if __name__ == "__main__":
    main() 