"""
Q&A Tools for RAG System

This file contains LangChain tools for:
- Search Tool: Find relevant document chunks
- Answer Tool: Generate answers using AI
"""

import os
import sys
import chromadb
from openai import OpenAI
from langchain.tools import tool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="../tools/chroma_db")
collection_name = "cybersecurity-story"

# Get ChromaDB collection
try:
    collection = chroma_client.get_collection(name=collection_name)
    print(f"✅ Connected to ChromaDB collection: {collection_name}")
except:
    print(f"❌ Collection {collection_name} not found!")
    print("Please run data_loader.py first to create the collection.")
    collection = None

# Initialize OpenAI client for embeddings
embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@tool
def search_documents(question: str) -> str:
    """
    Search for relevant document chunks based on the question.
    
    Args:
        question: The question to search for
        
    Returns:
        Relevant document chunks as a string
    """
    if not collection:
        return "Error: ChromaDB collection not found. Please run data_loader.py first."
    
    try:
        # Get embedding for the question using the same model as data_loader
        question_embedding = embedding_client.embeddings.create(
            model="text-embedding-3-small",
            input=question
        ).data[0].embedding
        
        # Query ChromaDB for relevant chunks
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=3
        )
        
        if not results['documents'][0]:
            return "No relevant documents found."
        
        # Combine relevant chunks
        relevant_chunks = "\n\n".join(results['documents'][0])
        
        return f"Found {len(results['documents'][0])} relevant chunks:\n\n{relevant_chunks}"
        
    except Exception as e:
        return f"Error searching documents: {str(e)}"

@tool
def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using AI based on the question and context.
    
    Args:
        question: The question to answer
        context: Relevant document chunks as context
        
    Returns:
        Generated answer from AI
    """
    try:
        # Create prompt for AI
        prompt = f"""You are a cybersecurity expert analyzing a cybersecurity incident. 
Answer the following question based on the provided context. 
Be accurate, concise, and provide specific details when available.

Context:
{context}

Question: {question}

Answer:"""
        
        # Generate answer using OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful cybersecurity expert assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def get_qa_tools():
    """Get all Q&A tools for use with agents"""
    return [search_documents, generate_answer]

# Test the tools
if __name__ == "__main__":
    print("🔍 Testing Q&A Tools...")
    
    # Test search tool
    print("\n1. Testing Search Tool:")
    question = "What time did the attack start?"
    search_result = search_documents.invoke(question)
    print(f"Question: {question}")
    print(f"Result: {search_result[:200]}...")
    
    # Test answer tool
    print("\n2. Testing Answer Tool:")
    context = "The attack started at 2:47 AM when jmalik connected via corp-vpn3."
    answer_result = generate_answer.invoke({"question": question, "context": context})
    print(f"Question: {question}")
    print(f"Context: {context}")
    print(f"Answer: {answer_result}")
    
    print("\n✅ Q&A Tools test complete!") 