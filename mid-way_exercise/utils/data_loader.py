import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
import re
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class StoryDataLoader:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "cybersecurity-story"
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-large")
    
    def parse_story_file(self, file_path):
        """Parse story file and extract the full text"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    
    def estimate_tokens(self, text):
        return len(self.tokenizer.encode(text))
    
    def create_chunks(self, story_text, chunk_size=400, chunk_overlap=80):
        """Create semantic chunks using RecursiveCharacterTextSplitter"""
        
        # Initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        # Split the text into chunks
        text_chunks = text_splitter.split_text(story_text)
        
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Clean up the chunk text
            cleaned_chunk = chunk_text.strip()
            if not cleaned_chunk:
                continue
                
            # Estimate tokens for this chunk
            token_count = self.estimate_tokens(cleaned_chunk)
            
            # Extract time information if present
            time_pattern = r'\b(?:At\s+)?\d{1,2}:\d{2}\s*(?:AM|PM)\b'
            times_in_chunk = re.findall(time_pattern, cleaned_chunk)
            
            chunks.append({
                'id': f"story_chunk_{i}",
                'text': cleaned_chunk,
                'metadata': {
                    'type': 'story_chunk',
                    'chunk_id': i,
                    'length': len(cleaned_chunk),
                    'token_estimate': token_count,
                    'has_time_marker': len(times_in_chunk) > 0,
                    'times_found': ', '.join(times_in_chunk) if times_in_chunk else '',
                    'document_title': 'The Day Everything Slowed Down',
                    'source': 'cybersecurity_incident_story'
                }
            })
        
        return chunks
    
    def get_embeddings(self, texts):
        """Batch embed using OpenAI"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=texts
        )
        return [e.embedding for e in response.data]
    
    def setup_chroma(self):
        """Initialize Chroma collection"""
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"Using existing Chroma collection: {self.collection_name}")
        except:
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Cybersecurity story text data"}
            )
            print(f"Created Chroma collection: {self.collection_name}")
        
        return collection
    
    def upload_to_chroma(self, chunks):
        """Upload chunks to Chroma with embeddings"""
        collection = self.setup_chroma()
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.get_embeddings(texts)
        ids = [chunk['id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"✅ Uploaded {len(chunks)} chunks to Chroma")
        return collection

def main():
    loader = StoryDataLoader()
    
    print("📂 Parsing story file...")
    story_text = loader.parse_story_file('../data/The_Day_Everything_Slowed_Down_Unstructured.txt')
    print(f"📏 Story length: {len(story_text)} characters")
    
    print("✂️ Creating chunks...")
    chunks = loader.create_chunks(story_text)
    print(f"🧩 Created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i + 1} (first 200 chars):")
        print(chunk['text'][:200] + "...")
    
    print("\n📤 Uploading to Chroma...")
    loader.upload_to_chroma(chunks)
    print("✅ Story data loading complete!")

if __name__ == "__main__":
    main()
