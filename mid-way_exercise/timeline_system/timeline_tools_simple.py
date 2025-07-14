from langchain.tools import tool
from timeline_map_reduce import map_reduce_timeline_function
from timeline_refine import refine_timeline_function
from file_utils import save_timeline_to_file
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@tool
def map_reduce_timeline(file_path: str) -> str:
    """
    Create a timeline summary using Map-Reduce method and save to file.
    
    Args:
        file_path: Path to the text file to summarize
        
    Returns:
        A timeline summary with bullet points organized chronologically
    """
    # Get timeline using map-reduce method
    timeline = map_reduce_timeline_function(file_path)
    
    # Save to file
    output_file = save_timeline_to_file(timeline, file_path, "map_reduce")
    
    return f"Timeline created using Map-Reduce method and saved to {output_file}:\n\n{timeline}"

@tool
def refine_timeline(file_path: str) -> str:
    """
    Create a timeline summary using Refine method and save to file.
    
    Args:
        file_path: Path to the text file to summarize
        
    Returns:
        A refined timeline summary with bullet points
    """
    # Get timeline using refine method
    timeline = refine_timeline_function(file_path)
    
    # Save to file
    output_file = save_timeline_to_file(timeline, file_path, "refine")
    
    return f"Timeline created using Refine method and saved to {output_file}:\n\n{timeline}"

def get_timeline_tools():
    """Get all timeline summarization tools for use with agents"""
    return [map_reduce_timeline, refine_timeline]

# Example usage
if __name__ == "__main__":
    # Example usage
    tools = get_timeline_tools()
    
    print("Available timeline tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Test with the house break-in story
    test_file = "house_break_in_story.txt"
    
    print(f"\nTesting timeline tools with {test_file}...")
    
    # Test map-reduce timeline
    print("\n1. Map-Reduce Timeline:")
    result1 = map_reduce_timeline(test_file)
    print(result1)
    
    # Test refine timeline
    print("\n2. Refine Timeline:")
    result2 = refine_timeline(test_file)
    print(result2) 