def save_timeline_to_file(timeline_content: str, file_path: str, method: str) -> str:
    """
    Save timeline content to a file with appropriate naming.
    
    Args:
        timeline_content: The timeline text to save
        file_path: Original file path
        method: The method used (map_reduce or refine)
        
    Returns:
        The output file path
    """
    # Create output filename
    base_name = file_path.replace('.txt', '')
    output_file = f"{method}_timeline_{base_name}.txt"
    
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