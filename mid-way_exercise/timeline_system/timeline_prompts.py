def create_extract_timeline_prompt():
    """Create a prompt specifically for timeline extraction with precision focus"""
    return """Extract and organize all chronological events from the following text into a clear timeline with bullet points. 

CRITICAL REQUIREMENTS:
1. Use EXACT times as mentioned in the text (e.g., "9:00 PM" not "around 9 PM")
2. Include specific actions and details (e.g., "called 911" not "contacted authorities")
3. Maintain chronological order precisely
4. Include all time markers mentioned
5. Be specific about who did what action

Format the timeline as:
• [EXACT TIME] - [SPECIFIC ACTION/EVENT]
• [EXACT TIME] - [SPECIFIC ACTION/EVENT]
• [EXACT TIME] - [SPECIFIC ACTION/EVENT]

If a time is not specified, use "Time not specified" but still include the event.

Text to analyze:
{text}

Timeline:"""

def create_improve_timeline_prompt():
    """Create a prompt for improving timeline summaries with precision focus"""
    return """You have an existing timeline summary and new information. Improve the timeline by:

PRECISION REQUIREMENTS:
1. Use EXACT times from the text (no approximations)
2. Include specific details and actions
3. Maintain chronological order
4. Add new events with precise timing
5. Correct any inaccuracies in the existing timeline
6. Be specific about actions and outcomes

Existing timeline:
{existing_summary}

New information to add:
{text}

Improved timeline (maintain bullet point format):"""

def create_merge_timeline_prompt():
    """Create a prompt for merging multiple timeline summaries with precision focus"""
    return """Merge these timeline summaries into one comprehensive chronological timeline with bullet points.

MERGE REQUIREMENTS:
1. Use EXACT times from all sources
2. Eliminate duplicates while preserving all unique events
3. Maintain precise chronological order
4. Include specific actions and details
5. Resolve any time conflicts by using the most specific time mentioned
6. Format as bullet points with exact times

Timeline summaries to merge:
{text}

Merged Timeline:""" 