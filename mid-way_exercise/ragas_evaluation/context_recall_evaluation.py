"""
Context Recall Evaluation for Q&A RAG System

Simple evaluation to check if we're retrieving ALL relevant information.
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

def check_chunk_contains_answer(question, chunk, expected_answer):
    """
    Check if a chunk contains the expected answer.
    Returns True if the chunk has the answer, False otherwise.
    """
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are checking if a document chunk contains the answer to a question.

Question: {question}
Expected Answer: {expected_answer}
Document Chunk: {chunk}

Does this chunk contain the expected answer?
- Return "YES" if the chunk contains the expected answer
- Return "NO" if the chunk does not contain the expected answer

Consider:
- Does the chunk mention the specific information from the expected answer?
- Is the information accurate and complete?
- Does it match what we're looking for?

Return only YES or NO:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an answer checker. Return only YES or NO."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        
        answer = response.choices[0].message.content.strip().upper()
        return answer == "YES"
        
    except Exception as e:
        print(f"Error checking answer: {e}")
        return False

def calculate_context_recall(question, chunks, expected_answer):
    """
    Calculate how much of the expected answer we found in our chunks.
    Returns a score between 0-1 (1 = found all the answer).
    """
    if not chunks:
        return 0.0
    
    # Check each chunk for the answer
    found_answers = 0
    for i, chunk in enumerate(chunks):
        has_answer = check_chunk_contains_answer(question, chunk, expected_answer)
        if has_answer:
            found_answers += 1
            print(f"  Chunk {i+1}: Contains answer ✓")
        else:
            print(f"  Chunk {i+1}: No answer ✗")
    
    # Calculate recall (how much of the answer we found)
    recall = found_answers / len(chunks) if chunks else 0.0
    return recall

def get_chunks_from_search(search_result):
    """
    Extract chunks from our search result.
    """
    if "Found" in search_result and "relevant chunks:" in search_result:
        chunks_text = search_result.split("relevant chunks:\n\n")[1]
        chunks = [chunk.strip() for chunk in chunks_text.split("\n\n") if chunk.strip()]
    else:
        chunks = [search_result]
    
    return chunks

def run_evaluation():
    """
    Run the context recall evaluation.
    """
    # Test questions with expected answers
    test_questions = [
        {
            "question": "What time did the attack start?",
            "expected": "The attack started at 3:13 AM when logi_loader.dll was copied to four separate machines."
        },
        {
            "question": "Who was the main suspect?",
            "expected": "The main suspect was jmalik who connected via corp-vpn3 at 2:47 AM."
        },
        {
            "question": "What was the name of the suspicious file?",
            "expected": "The suspicious file was called logi_loader.dll."
        },
        {
            "question": "What happened at 4:55 PM?",
            "expected": "At 4:55 PM, they joined an emergency call with Legal, security, and VPs to discuss unauthorized access and credential compromise."
        },
        {
            "question": "Who were in the emergency call?",
            "expected": "Legal, security, and two VPs were in the emergency call."
        }
    ]
    
    print("🔍 Context Recall Evaluation")
    print("=" * 50)
    
    all_scores = []
    results = []
    
    # Test each question
    for i, test_case in enumerate(test_questions, 1):
        question = test_case["question"]
        expected = test_case["expected"]
        
        print(f"\n{i}. Question: {question}")
        print(f"   Expected: {expected}")
        
        try:
            # Get chunks using our search
            search_result = search_documents(question)
            chunks = get_chunks_from_search(search_result)
            
            print(f"   Retrieved {len(chunks)} chunks")
            
            # Calculate recall
            recall = calculate_context_recall(question, chunks, expected)
            all_scores.append(recall)
            
            results.append({
                "question": question,
                "expected_answer": expected,
                "recall": recall,
                "num_chunks": len(chunks)
            })
            
            print(f"   Context Recall: {recall:.3f}")
            
        except Exception as e:
            print(f"   Error: {e}")
            all_scores.append(0.0)
    
    # Calculate overall score
    overall_recall = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    print(f"\n{'='*50}")
    print(f"Overall Context Recall: {overall_recall:.3f}")
    print(f"Questions tested: {len(test_questions)}")
    
    # Save results
    output = {
        "overall_recall": overall_recall,
        "question_results": results
    }
    
    with open("context_recall_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: context_recall_results.json")
    
    # Show summary
    print(f"\n📊 Summary:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['question'][:40]}... - {result['recall']:.3f}")

if __name__ == "__main__":
    run_evaluation() 