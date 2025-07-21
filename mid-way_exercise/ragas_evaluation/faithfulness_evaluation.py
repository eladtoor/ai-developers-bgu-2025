"""
Faithfulness Evaluation for Q&A RAG System

Simple evaluation to check if our answers are based on retrieved context.
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

from tools.rerank_qa_tools import rerank_search_documents, generate_answer

# Load environment variables
load_dotenv()

def check_answer_faithfulness(question, context, generated_answer):
    """
    Check if the generated answer is faithful to the provided context.
    Returns a score between 0-1 (1 = completely faithful).
    """
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are checking if an answer is based on the given context.

Question: {question}

Context: {context}

Generated Answer: {generated_answer}

Rate how faithful the answer is to the context (0-1):
- 0: Answer is completely made up, not in context
- 0.5: Answer is partially based on context, some details added
- 1: Answer is completely based on context, no extra information

Consider:
- Does the answer contain information from the context?
- Are there facts in the answer that aren't in the context?
- Is the answer accurate to what's in the context?

Return only a number between 0 and 1:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a faithfulness checker. Return only a number between 0 and 1."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        
        score_text = response.choices[0].message.content.strip()
        score = float(score_text)
        return max(0, min(1, score))  # Make sure it's between 0-1
        
    except Exception as e:
        print(f"Error checking faithfulness: {e}")
        return 0.5

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

def combine_chunks(chunks):
    """
    Combine all chunks into one context string.
    """
    return "\n\n".join(chunks)

def run_evaluation():
    """
    Run the faithfulness evaluation.
    """
    # Test questions
    test_questions = [
        "What time did the attack start?",
        "Who was the main suspect?", 
        "What was the name of the suspicious file?",
        "What happened at 4:55 PM?",
        "Who were in the emergency call?"
    ]
    
    print("🔍 Faithfulness Evaluation")
    print("=" * 50)
    
    all_scores = []
    results = []
    
    # Test each question
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        try:
            # Step 1: Get context chunks
            search_result = rerank_search_documents(question)
            chunks = get_chunks_from_search(search_result)
            context = combine_chunks(chunks)
            
            print(f"   Retrieved {len(chunks)} chunks")
            
            # Step 2: Generate answer using our RAG system
            # Use the proper LangChain tool invocation
            generated_answer = generate_answer.invoke({"question": question, "context": context})
            
            print(f"   Generated answer: {generated_answer[:100]}...")
            
            # Step 3: Check faithfulness
            faithfulness = check_answer_faithfulness(question, context, generated_answer)
            all_scores.append(faithfulness)
            
            results.append({
                "question": question,
                "faithfulness": faithfulness,
                "num_chunks": len(chunks),
                "generated_answer": generated_answer
            })
            
            print(f"   Faithfulness: {faithfulness:.3f}")
            
        except Exception as e:
            print(f"   Error: {e}")
            all_scores.append(0.0)
    
    # Calculate overall score
    overall_faithfulness = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    print(f"\n{'='*50}")
    print(f"Overall Faithfulness: {overall_faithfulness:.3f}")
    print(f"Questions tested: {len(test_questions)}")
    
    # Save results
    output = {
        "overall_faithfulness": overall_faithfulness,
        "question_results": results
    }
    
    with open("faithfulness_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: faithfulness_results.json")
    
    # Show summary
    print(f"\n📊 Summary:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['question'][:40]}... - {result['faithfulness']:.3f}")

if __name__ == "__main__":
    run_evaluation() 