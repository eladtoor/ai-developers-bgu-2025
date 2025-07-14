from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from timeline_tools_simple import get_timeline_tools
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_simple_timeline_agent():
    """Create a simple agent that only does timeline summarization"""
    
    # Get timeline tools
    tools = get_timeline_tools()
    
    # Create the language model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a timeline summarization agent. Your job is to take a text file and create timeline summaries using both Map-Reduce and Refine methods.

Available Tools:
- map_reduce_timeline: Create timeline with bullet points using Map-Reduce method
- refine_timeline: Create timeline with bullet points using Refine method

When a user provides a text file, you should:
1. Use map_reduce_timeline to create a timeline summary
2. Use refine_timeline to create a timeline summary
3. Save both results to separate files

Always ask for the file path if it's not provided."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

def main():
    """Main function to run the simple timeline agent"""
    
    print("="*60)
    print("SIMPLE TIMELINE SUMMARIZATION AGENT")
    print("="*60)
    print("\nThis agent will:")
    print("1. Take a text file as input")
    print("2. Create timeline summaries using Map-Reduce method")
    print("3. Create timeline summaries using Refine method")
    print("4. Save both results to separate files")
    
    print("\n📁 Available documents:")
    print("- car_insurance_document.txt")
    print("- house_break_in_story.txt")
    print("- Or provide your own file path")
    
    print("\nExample usage:")
    print("- 'Process house_break_in_story.txt'")
    print("- 'Create timelines from car_insurance_document.txt'")
    print("- 'Summarize timeline from my_file.txt'")
    
    print("\nType 'quit' to exit")
    print("-"*60)
    
    # Create the agent
    agent = create_simple_timeline_agent()
    
    # Start conversation
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        try:
            # Run the agent
            response = agent.invoke({"input": user_input})
            print(f"\nAssistant: {response['output']}")
            
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different request.")

if __name__ == "__main__":
    main() 