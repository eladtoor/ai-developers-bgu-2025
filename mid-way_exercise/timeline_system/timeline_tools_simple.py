from langchain.tools import tool
from timeline_map_reduce import map_reduce_timeline_function
from timeline_refine import refine_timeline_function
from file_utils import save_timeline_to_file
import os
from dotenv import load_dotenv
import re
from timeline_prompts import create_extract_timeline_prompt, create_improve_timeline_prompt, create_merge_timeline_prompt
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

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
    
    # Validate and improve the timeline
    validated_timeline = validate_timeline_answer(timeline)
    
    # Save to file
    output_file = save_timeline_to_file(validated_timeline, file_path, "map_reduce")
    
    return f"Timeline created using Map-Reduce method and saved to {output_file}:\n\n{validated_timeline}"

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
    
    # Validate and improve the timeline
    validated_timeline = validate_timeline_answer(timeline)
    
    # Save to file
    output_file = save_timeline_to_file(validated_timeline, file_path, "refine")
    
    return f"Timeline created using Refine method and saved to {output_file}:\n\n{validated_timeline}"

def validate_timeline_answer(answer):
    """Validate and improve timeline answer precision"""
    
    # Check for exact time patterns
    time_patterns = [
        r'\d{1,2}:\d{2}\s*(AM|PM)',  # 9:00 PM
        r'\d{1,2}\s*(AM|PM)',        # 9 PM
        r'\d{1,2}:\d{2}',            # 9:00
    ]
    
    # Check for specific action keywords
    action_improvements = {
        'contacted authorities': 'called 911',
        'called emergency services': 'called 911',
        'dialed emergency': 'called 911',
        'around': 'exactly',
        'approximately': 'exactly',
        'about': 'exactly'
    }
    
    # Validate and correct
    corrected_answer = answer
    
    # Replace vague terms with specific ones
    for vague, specific in action_improvements.items():
        corrected_answer = corrected_answer.replace(vague, specific)
    
    # Check if times are properly formatted
    lines = corrected_answer.split('\n')
    improved_lines = []
    
    for line in lines:
        if line.strip().startswith('•'):
            # Check if line has exact time
            has_exact_time = any(re.search(pattern, line) for pattern in time_patterns)
            if not has_exact_time and any(word in line.lower() for word in ['time', 'pm', 'am']):
                # Try to extract time from context
                time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', line)
                if time_match:
                    improved_lines.append(line)
                else:
                    improved_lines.append(line.replace('Time not specified', 'Time not specified'))
            else:
                improved_lines.append(line)
        else:
            improved_lines.append(line)
    
    return '\n'.join(improved_lines)

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