from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path so we can import from it
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from tools.timeline_tools import get_timeline_tools
from tools.qa_tools import get_qa_tools
from tools.query_router import classify_question

# Load environment variables from project root
load_dotenv(dotenv_path=project_root.parent / ".env")

def create_story_analysis_agent():
    """Create a story analysis agent that can do timeline summarization and RAG Q&A"""
    
    # Get all tools
    timeline_tools = get_timeline_tools()
    qa_tools = get_qa_tools()
    all_tools = timeline_tools + qa_tools
    
    # Create the language model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a story analysis agent. Your job is to handle two types of requests:

1. TIMELINE REQUESTS: Create timeline summaries using Map-Reduce and Refine methods
2. RAG Q&A REQUESTS: Answer specific questions about the cybersecurity incident

Available Timeline Tools:
- map_reduce_timeline: Create timeline with bullet points using Map-Reduce method
- refine_timeline: Create timeline with bullet points using Refine method

Available RAG Tools:
- search_documents: Find relevant document chunks for a question
- generate_answer: Generate answer using AI based on context

CRITICAL RULES:
- For TIMELINE requests ONLY: Use map_reduce_timeline and refine_timeline tools
- For RAG Q&A requests ONLY: Use search_documents and generate_answer tools
- NEVER use both timeline and RAG tools for the same request
- NEVER create timelines when answering Q&A questions
- NEVER answer Q&A questions when creating timelines
- STOP after completing the appropriate tools for the request type
- DO NOT continue with additional tools after completing the request

For TIMELINE requests:
- Use ONLY map_reduce_timeline and refine_timeline
- Save both results to separate files
- Do NOT use any RAG tools
- STOP after creating both timelines

For RAG Q&A requests:
- Use ONLY search_documents to find relevant chunks
- Use ONLY generate_answer to create the final answer
- Do NOT use any timeline tools
- STOP after generating the answer

Available documents:
- "The_Day_Everything_Slowed_Down.txt" (in data folder)

IMPORTANT: Always pass just the filename (e.g., "The_Day_Everything_Slowed_Down.txt"), not the full path.

Always ask for the file path if it's not provided."""),
        ("human", "Request type: {request_type}\nUser question: {input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, all_tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True, handle_parsing_errors=True)
    
    return agent_executor

def main():
    """Main function to run the story analysis agent"""
    
    print("="*60)
    print("STORY ANALYSIS AGENT")
    print("="*60)
    print("\nThis agent can handle two types of requests:")
    print("\n📋 TIMELINE REQUESTS:")
    print("1. Create timeline summaries using Map-Reduce method")
    print("2. Create timeline summaries using Refine method")
    print("3. Save both results to separate files")
    
    print("\n🔍 RAG Q&A REQUESTS:")
    print("1. Answer specific questions about the cybersecurity incident")
    print("2. Find relevant information from the document")
    print("3. Generate detailed answers using AI")
    
    print("\n📁 Available documents:")
    print("- The Day Everything Slowed Down (The_Day_Everything_Slowed_Down.txt)")
    print("- Or provide your own file path")
    
    print("\nExample usage:")
    print("- 'Create a timeline of The Day Everything Slowed Down'")
    print("- 'What time did the attack start?'")
    print("- 'Who was the main suspect?'")
    print("- 'What was the name of the suspicious file?'")
    
    print("\nType 'quit' to exit")
    print("-"*60)
    
    # Create the agent
    agent = create_story_analysis_agent()
    
    # Start conversation
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        try:
            # Classify the question first
            classification = classify_question(user_input)
            print(f"\n🔍 Question type: {classification.upper()}")
            
            # Pass the classification to the agent
            response = agent.invoke({
                "input": user_input,
                "request_type": classification.upper()
            })
            print(f"\nAssistant: {response['output']}")
            
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different request.")
            print("If you're asking a Q&A question, try rephrasing it more clearly.")

if __name__ == "__main__":
    main() 