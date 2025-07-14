import os
import time
from dotenv import load_dotenv
from stuff_summarization import StuffSummarization
from map_reduce_summarization import MapReduceSummarization

load_dotenv()

def compare_summarization_approaches():
    """Compare the two summarization approaches"""
    
    print("🔍 Comparing Summarization Approaches")
    print("=" * 50)
    print("Document: LLM-Powered Autonomous Agents")
    print("URL: https://lilianweng.github.io/posts/2023-06-23-agent/")
    print()
    
    # Test Stuff Summarization
    print("📋 Approach 1: Stuff Summarization")
    print("-" * 30)
    print("• Puts entire document in one prompt")
    print("• Simple and straightforward")
    print("• Limited by token context window")
    print("• May lose detail for very long documents")
    print()
    
    start_time = time.time()
    stuff_summarizer = StuffSummarization()
    stuff_summary = stuff_summarizer.run_stuff_summarization()
    stuff_time = time.time() - start_time
    
    print(f"⏱️  Stuff summarization completed in {stuff_time:.2f} seconds")
    print()
    
    # Test Map-Reduce Summarization
    print("🗺️ Approach 2: Map-Reduce Summarization")
    print("-" * 30)
    print("• Splits document into chunks")
    print("• Summarizes each chunk separately (Map)")
    print("• Combines summaries into final summary (Reduce)")
    print("• Handles longer documents better")
    print("• More complex but more scalable")
    print()
    
    start_time = time.time()
    map_reduce_summarizer = MapReduceSummarization()
    map_reduce_summary = map_reduce_summarizer.run_map_reduce_summarization()
    map_reduce_time = time.time() - start_time
    
    print(f"⏱️  Map-reduce summarization completed in {map_reduce_time:.2f} seconds")
    print()
    
    # Comparison
    print("📊 Comparison Results")
    print("=" * 30)
    print(f"Stuff Approach:")
    print(f"  • Time: {stuff_time:.2f} seconds")
    print(f"  • Simplicity: High")
    print(f"  • Scalability: Low")
    print(f"  • Detail preservation: Medium")
    print()
    print(f"Map-Reduce Approach:")
    print(f"  • Time: {map_reduce_time:.2f} seconds")
    print(f"  • Simplicity: Medium")
    print(f"  • Scalability: High")
    print(f"  • Detail preservation: High")
    print()
    
    # Save comparison report
    with open("comparison_report.txt", "w", encoding="utf-8") as f:
        f.write("Summarization Approaches Comparison\n")
        f.write("=" * 40 + "\n\n")
        f.write("Document: LLM-Powered Autonomous Agents\n")
        f.write("URL: https://lilianweng.github.io/posts/2023-06-23-agent/\n\n")
        
        f.write("STUFF SUMMARIZATION:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Time: {stuff_time:.2f} seconds\n")
        f.write("Pros:\n")
        f.write("• Simple implementation\n")
        f.write("• Fast for short documents\n")
        f.write("• Single API call\n")
        f.write("Cons:\n")
        f.write("• Limited by token context\n")
        f.write("• May lose detail in long documents\n")
        f.write("• Not scalable\n\n")
        
        f.write("MAP-REDUCE SUMMARIZATION:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Time: {map_reduce_time:.2f} seconds\n")
        f.write("Pros:\n")
        f.write("• Handles long documents\n")
        f.write("• Scalable approach\n")
        f.write("• Better detail preservation\n")
        f.write("• Parallel processing possible\n")
        f.write("Cons:\n")
        f.write("• More complex implementation\n")
        f.write("• Multiple API calls\n")
        f.write("• Slower for short documents\n\n")
        
        f.write("RECOMMENDATION:\n")
        f.write("-" * 15 + "\n")
        if len(stuff_summary) < 8000:  # Rough estimate for token limit
            f.write("Use Stuff approach for shorter documents (< 8000 characters)\n")
        else:
            f.write("Use Map-Reduce approach for longer documents (> 8000 characters)\n")
    
    print("✅ Comparison report saved to lecture9/comparison_report.txt")
    
    return {
        "stuff_time": stuff_time,
        "map_reduce_time": map_reduce_time,
        "stuff_summary": stuff_summary,
        "map_reduce_summary": map_reduce_summary
    }

def analyze_summary_quality(summaries):
    """Analyze the quality of both summaries"""
    
    print("\n🔍 Summary Quality Analysis")
    print("=" * 30)
    
    stuff_summary = summaries["stuff_summary"]
    map_reduce_summary = summaries["map_reduce_summary"]
    
    # Basic metrics
    stuff_length = len(stuff_summary)
    map_reduce_length = len(map_reduce_summary)
    
    print(f"Stuff Summary Length: {stuff_length} characters")
    print(f"Map-Reduce Summary Length: {map_reduce_length} characters")
    print()
    
    # Content analysis
    print("Content Coverage Analysis:")
    print("-" * 25)
    
    # Check for key topics
    key_topics = [
        "agent", "autonomous", "LLM", "language model", "architecture",
        "memory", "planning", "tool use", "reasoning", "reflection"
    ]
    
    for topic in key_topics:
        stuff_count = stuff_summary.lower().count(topic)
        map_reduce_count = map_reduce_summary.lower().count(topic)
        
        print(f"{topic}: Stuff={stuff_count}, Map-Reduce={map_reduce_count}")
    
    print()
    print("📝 Summary files created:")
    print("  • lecture9/stuff_summary.txt")
    print("  • lecture9/map_reduce_summary.txt")
    print("  • lecture9/comparison_report.txt")

if __name__ == "__main__":
    results = compare_summarization_approaches()
    analyze_summary_quality(results) 