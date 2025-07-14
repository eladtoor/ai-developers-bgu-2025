def create_extract_timeline_prompt():
    """Create a prompt specifically for timeline extraction"""
    return """Extract and organize all chronological events from the following text into a clear timeline with bullet points. Focus on:

1. Specific times and dates mentioned
2. Sequential order of events
3. Key actions and decisions
4. Important turning points
5. Duration of processes or phases

Format the timeline as:
• [Time] - [Event/Action]
• [Time] - [Event/Action]
• [Time] - [Event/Action]

Text to analyze:
{text}

Timeline:"""

def create_improve_timeline_prompt():
    """Create a prompt for improving timeline summaries"""
    return """You have an existing timeline summary and new information. Improve the timeline by:

1. Adding new chronological events from the new information
2. Maintaining the bullet point format
3. Ensuring proper chronological order
4. Keeping important time markers
5. Combining related events when appropriate

Existing timeline:
{existing_summary}

New information to add:
{text}

Improved timeline:"""

def create_merge_timeline_prompt():
    """Create a prompt for merging multiple timeline summaries"""
    return """Merge these timeline summaries into one comprehensive chronological timeline with bullet points:

{text}

Merged Timeline:""" 