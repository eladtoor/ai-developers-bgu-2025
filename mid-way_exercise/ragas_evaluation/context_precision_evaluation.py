"""
Context Precision Evaluation for Q&A RAG System

Simple evaluation to check if retrieved chunks are relevant to questions.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.qa_tools import search_documents

# Load environment variables
load_dotenv()

def evaluate_chunk_relevance(question, chunk):
    """
    Check if a chunk is relevant to a question.
    Returns a score between 0-1 (1 = very relevant).
    """
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are checking if a document chunk is relevant to a question.

Question: {question}

Document Chunk: {chunk}

Rate how relevant this chunk is to the question (0-1):
- 0: Not relevant at all
- 0.5: Somewhat relevant  
- 1: Very relevant, contains direct answer

Return only a number between 0 and 1:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a relevance checker. Return only a number between 0 and 1."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        
        score_text = response.choices[0].message.content.strip()
        score = float(score_text)
        return max(0, min(1, score))  # Make sure it's between 0-1
        
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return 0.5

def calculate_context_precision(question, chunks):
    """
    Calculate how precise our retrieved chunks are for a question.
    Returns a score between 0-1 (1 = all chunks are relevant).
    """
    if not chunks:
        return 0.0
    
    # Check relevance of each chunk
    scores = []
    for i, chunk in enumerate(chunks):
        score = evaluate_chunk_relevance(question, chunk)
        scores.append(score)
        print(f"  Chunk {i+1} relevance: {score:.3f}")
    
    # Average all scores
    precision = sum(scores) / len(scores)
    return precision

def get_chunks_from_search(search_result):
    """
    Extract chunks from our search result.
    """
    if "Found" in search_result and "relevant chunks:" in search_result:
        # Get the chunks part
        chunks_text = search_result.split("relevant chunks:\n\n")[1]
        # Split into individual chunks
        chunks = [chunk.strip() for chunk in chunks_text.split("\n\n") if chunk.strip()]
    else:
        chunks = [search_result]
    
    return chunks

def run_evaluation():
    """
    Run the context precision evaluation.
    """
    # Test questions
    test_questions = [
        "What time did the attack start?",
        "Who was the main suspect?", 
        "What was the name of the suspicious file?",
        "What happened at 4:55 PM?",
        "Who were in the emergency call?"
    ]
    
    print("🔍 Context Precision Evaluation")
    print("=" * 50)
    
    all_scores = []
    results = []
    
    # Test each question
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        try:
            # Get chunks using our search
            search_result = search_documents(question)
            chunks = get_chunks_from_search(search_result)
            
            print(f"   Retrieved {len(chunks)} chunks")
            
            # Calculate precision
            precision = calculate_context_precision(question, chunks)
            all_scores.append(precision)
            
            results.append({
                "question": question,
                "precision": precision,
                "num_chunks": len(chunks)
            })
            
            print(f"   Context Precision: {precision:.3f}")
            
        except Exception as e:
            print(f"   Error: {e}")
            all_scores.append(0.0)
    
    # Calculate overall score
    overall_precision = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    print(f"\n{'='*50}")
    print(f"Overall Context Precision: {overall_precision:.3f}")
    print(f"Questions tested: {len(test_questions)}")
    
    # Save results
    output = {
        "overall_precision": overall_precision,
        "question_results": results
    }
    
    with open("context_precision_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: context_precision_results.json")
    
    # Show summary
    print(f"\n📊 Summary:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['question'][:40]}... - {result['precision']:.3f}")

if __name__ == "__main__":
    run_evaluation() 