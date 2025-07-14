import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

class ContextAwareTimelineSummarizer:
    def __init__(self):
        """Initialize the summarizer with OpenAI model."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=4000
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_document(self, file_path):
        """Load document from file."""
        print(f"📄 Loading document: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Loaded document ({len(content)} characters)")
            return content
        except FileNotFoundError:
            print(f"❌ Error: File {file_path} not found")
            return None
        except Exception as e:
            print(f"❌ Error loading document: {e}")
            return None
    
    def create_timeline_prompt(self, current_timeline, new_chunk, chunk_num, total_chunks):
        """Create a prompt for timeline refinement."""
        system_prompt = """You are a historical timeline expert. Your task is to create and refine chronological timelines that are context-aware and nuanced.

IMPORTANT GUIDELINES:
1. Maintain chronological order and logical flow
2. Show cause-and-effect relationships between events
3. Include context that explains WHY events happened, not just WHAT happened
4. Connect events across time periods to show historical continuity
5. Highlight turning points and their significance
6. Use clear, concise language while preserving important details
7. Format as a clear timeline with dates/periods and descriptions

For each refinement:
- Integrate new information with existing timeline
- Update context and connections as needed
- Maintain the narrative flow and historical perspective
- Ensure events are properly contextualized within their historical period"""

        user_prompt = f"""Here is the current timeline summary so far (covering {chunk_num-1} of {total_chunks} sections):

{current_timeline}

Now I'm adding information from section {chunk_num} of {total_chunks}:

{new_chunk}

Please update and expand the timeline, integrating the new historical information. Focus on:
1. Adding new events in chronological order
2. Updating context and connections between events
3. Showing how new events relate to previously mentioned ones
4. Maintaining the historical narrative flow
5. Highlighting significant developments and turning points

Provide a comprehensive, context-aware timeline that tells the complete story so far."""

        return system_prompt, user_prompt
    
    def refine_timeline(self, current_timeline, new_chunk, chunk_num, total_chunks):
        """Refine the timeline with new information."""
        system_prompt, user_prompt = self.create_timeline_prompt(
            current_timeline, new_chunk, chunk_num, total_chunks
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"❌ Error during timeline refinement: {e}")
            return current_timeline
    
    def create_initial_timeline(self, first_chunk):
        """Create the initial timeline from the first chunk."""
        system_prompt = """You are a historical timeline expert. Create an initial timeline from the first section of a historical document.

IMPORTANT GUIDELINES:
1. Extract all chronological events and developments
2. Organize them in clear chronological order
3. Include context and significance for major events
4. Show the historical narrative flow
5. Use clear formatting with dates/periods and descriptions
6. Focus on establishing the foundation for the historical story

Format the timeline clearly and comprehensively."""

        user_prompt = f"""Create an initial timeline from this first section of historical content:

{first_chunk}

Extract all chronological events, developments, and significant moments. Organize them in a clear timeline format that establishes the foundation for the historical narrative."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"❌ Error creating initial timeline: {e}")
            return "Initial timeline could not be generated."
    
    def run_context_aware_timeline_summarization(self, file_path, output_file="context_aware_timeline.txt"):
        """Run the context-aware timeline summarization process."""
        print("🤖 Generating context-aware timeline using iterative refinement...")
        
        # Load document
        document = self.load_document(file_path)
        if not document:
            return None
        
        # Split document into chunks
        chunks = self.text_splitter.split_text(document)
        print(f"📄 Split document into {len(chunks)} chunks")
        
        # Initialize timeline
        print("🔄 Starting context-aware timeline extraction...")
        current_timeline = self.create_initial_timeline(chunks[0])
        print(f"✅ Initial timeline generated ({len(current_timeline)} characters)")
        
        # Iteratively refine timeline with each chunk
        for i, chunk in enumerate(chunks[1:], 2):
            print(f"🔄 Refining timeline with chunk {i}/{len(chunks)}...")
            current_timeline = self.refine_timeline(
                current_timeline, chunk, i, len(chunks)
            )
            print(f"✅ Timeline refined ({len(current_timeline)} characters)")
        
        # Save final timeline
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(current_timeline)
            print(f"✅ Context-aware timeline saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving timeline: {e}")
            return None
        
        # Print preview
        print("\n📋 Context-Aware Timeline Preview:")
        print("=" * 50)
        preview_lines = current_timeline.split('\n')[:20]
        for line in preview_lines:
            print(line)
        if len(current_timeline.split('\n')) > 20:
            print("...")
        
        return current_timeline

def main():
    """Main function to run the context-aware timeline summarization."""
    summarizer = ContextAwareTimelineSummarizer()
    
    # Run summarization on the Israel history document
    result = summarizer.run_context_aware_timeline_summarization(
        "israel_history_document.txt",
        "israel_context_aware_timeline.txt"
    )
    
    if result:
        print("\n✅ Context-aware timeline summarization completed successfully!")
        print(f"📄 Timeline saved to: israel_context_aware_timeline.txt")
    else:
        print("\n❌ Timeline summarization failed.")

if __name__ == "__main__":
    main() 