"""
Reranked Q&A Tools for RAG System

This file contains LangChain tools with reranking to improve retrieval precision.
"""

import os
import sys
import chromadb
import re
from openai import OpenAI
from langchain.tools import tool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="../utils/chroma_db")
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

def extract_time_from_question(question):
    """Extract time patterns from question"""
    time_pattern = r'\b(?:At\s+)?\d{1,2}:\d{2}\s*(?:AM|PM)\b'
    times = re.findall(time_pattern, question)
    return times

def extract_keywords_from_question(question):
    """Extract important keywords from question"""
    # Remove common question words
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'did', 'happened', 'at', 'in', 'on']
    words = question.lower().split()
    keywords = [word for word in words if word not in question_words and len(word) > 2]
    return keywords

def rerank_chunks(chunks, distances, question):
    """
    Rerank chunks based on question-specific criteria
    """
    # Extract patterns from question
    times = extract_time_from_question(question)
    keywords = extract_keywords_from_question(question)
    
    # Create list of (chunk, distance, score) tuples
    chunk_scores = []
    
    for chunk, distance in zip(chunks, distances):
        score = 1.0 / (1.0 + distance)  # Convert distance to similarity score
        
        # Boost score for chunks containing specific times
        if times:
            for time in times:
                if time in chunk:
                    score *= 2.0  # Double the score
                    print(f"🎯 Boosted chunk containing '{time}'")
        
        # Boost score for chunks containing keywords
        if keywords:
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in chunk.lower())
            if keyword_matches > 0:
                score *= (1.0 + keyword_matches * 0.3)  # Boost by 30% per keyword
                print(f"🔑 Boosted chunk with {keyword_matches} keyword matches")
        
        # Boost score for chunks containing temporal markers
        temporal_markers = ['time', 'when', 'at', 'pm', 'am', 'emergency', 'call']
        temporal_matches = sum(1 for marker in temporal_markers if marker.lower() in chunk.lower())
        if temporal_matches > 0:
            score *= (1.0 + temporal_matches * 0.1)  # Small boost for temporal content
        
        chunk_scores.append((chunk, distance, score))
    
    # Sort by score (highest first)
    chunk_scores.sort(key=lambda x: x[2], reverse=True)
    
    # Return top 2 chunks after reranking
    return [chunk for chunk, distance, score in chunk_scores[:2]]

@tool
def rerank_search_documents(question: str) -> str:
    """
    Search for relevant document chunks using semantic search with reranking.
    
    Args:
        question: The question to search for
        
    Returns:
        Relevant document chunks as a string
    """
    if not collection:
        return "Error: ChromaDB collection not found. Please run data_loader.py first."
    
    try:
        print(f"🔍 Reranked search for: '{question}'")
        
        # Step 1: Semantic search with more results
        question_embedding = embedding_client.embeddings.create(
            model="text-embedding-3-large",
            input=question
        ).data[0].embedding
        
        # Get more candidates for reranking
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=8  # Get more candidates
        )
        
        chunks = results['documents'][0] if results['documents'][0] else []
        distances = results['distances'][0] if results['distances'][0] else []
        
        print(f"📊 Retrieved {len(chunks)} candidates for reranking")
        
        if not chunks:
            return "No relevant documents found."
        
        # Step 2: Rerank chunks
        reranked_chunks = rerank_chunks(chunks, distances, question)
        
        print(f"🎯 Selected {len(reranked_chunks)} chunks after reranking")
        
        # Combine relevant chunks
        relevant_chunks = "\n\n".join(reranked_chunks)
        
        return f"Found {len(reranked_chunks)} relevant chunks (reranked):\n\n{relevant_chunks}"
        
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

def get_rerank_qa_tools():
    """Get all reranked Q&A tools for use with agents"""
    return [rerank_search_documents, generate_answer]

# Test the tools
if __name__ == "__main__":
    print("🔍 Testing Reranked Q&A Tools...")
    
    # Test reranked search tool
    print("\n1. Testing Reranked Search Tool:")
    question = "What happened at 4:55 PM?"
    search_result = rerank_search_documents.invoke(question)
    print(f"Question: {question}")
    print(f"Result: {search_result[:200]}...")
    
    # Test answer tool
    print("\n2. Testing Answer Tool:")
    context = "4:55 PM, I joined the emergency call. Legal, security, and two of the VPs were on."
    answer_result = generate_answer.invoke({"question": question, "context": context})
    print(f"Question: {question}")
    print(f"Context: {context}")
    print(f"Answer: {answer_result}")
    
    print("\n✅ Reranked Q&A Tools test complete!") 