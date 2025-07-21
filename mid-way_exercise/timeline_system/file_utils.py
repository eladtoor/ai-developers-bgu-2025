def save_timeline_to_file(timeline_content: str, file_path: str, method: str) -> str:
    """
    Save timeline content to a file with timestamp to avoid overwriting.
    
    Args:
        timeline_content: The timeline text to save
        file_path: Original file path
        method: The method used (map_reduce or refine)
        
    Returns:
        The output file path
    """
    import os
    from datetime import datetime
    
    # Create outputs directory in agents folder if it doesn't exist
    current_dir = os.getcwd()
    if 'agents' in current_dir:
        # We're in the agents directory
        summaries_dir = "outputs"
    elif 'tools' in current_dir:
        # We're in the tools directory, go to agents/outputs
        summaries_dir = os.path.join("..", "agents", "outputs")
    else:
        # Default to timeline_summaries
        summaries_dir = "timeline_summaries"
    
    if not os.path.exists(summaries_dir):
        os.makedirs(summaries_dir)
    
    # Extract just the filename without path
    filename = os.path.basename(file_path)
    base_name = filename.replace('.txt', '')
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(summaries_dir, f"{method}_timeline_{base_name}_{timestamp}.txt")
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(timeline_content)
    
    return output_file

def load_document(file_path: str) -> str:
    """
    Load text from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        The text content of the file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read() 