import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Literal, TypedDict
from langchain_core.runnables import RunnableConfig

load_dotenv()

class TimelineSummarization:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200
        )
        
    def load_dota2_document(self):
        """Load the Dota 2 comprehensive document"""
        try:
            with open("dota2_comprehensive_document.txt", "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error loading document: {e}")
            return None
    
    def create_documents(self, content):
        """Create LangChain documents from the content"""
        return Document(
            page_content=content,
            metadata={"source": "dota2_comprehensive_document.txt"}
        )
    
    def split_document_into_chunks(self, document):
        """Split the document into smaller chunks for iterative processing"""
        chunks = self.text_splitter.split_documents([document])
        return [chunk.page_content for chunk in chunks]
    
    def create_initial_timeline_chain(self):
        """Create the initial timeline extraction chain"""
        summarize_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert timeline analyst. Extract and organize timeline information from the given text about Dota 2 history.
            
            Focus on:
            - Exact dates and years
            - Major events, releases, and tournaments
            - Chronological order of events
            - Key milestones and developments
            
            Create a clear, chronological timeline with specific dates."""),
            ("human", "Extract timeline information from the following text: {context}")
        ])
        
        return summarize_prompt | self.llm | StrOutputParser()
    
    def create_refine_timeline_chain(self):
        """Create the timeline refinement chain"""
        refine_template = """
        You are an expert timeline analyst. Refine and expand the existing timeline with new information.
        
        Existing timeline:
        {existing_answer}
        
        New context:
        ------------
        {context}
        ------------
        
        Given the new context, refine and expand the timeline. Ensure all dates are accurate and events are in chronological order. Add new events and details while maintaining the timeline structure.
        
        Focus on:
        - Chronological accuracy
        - Complete date information
        - Major milestones and events
        - Clear timeline progression
        """
        
        refine_prompt = ChatPromptTemplate.from_messages([
            ("human", refine_template)
        ])
        
        return refine_prompt | self.llm | StrOutputParser()
    
    async def iterative_timeline_summarize(self, chunks):
        """Perform iterative timeline summarization"""
        
        if not chunks:
            return "No content to analyze."
        
        print(f"🔄 Starting timeline extraction with {len(chunks)} chunks...")
        
        # Create chains
        initial_timeline_chain = self.create_initial_timeline_chain()
        refine_timeline_chain = self.create_refine_timeline_chain()
        
        # Generate initial timeline from first chunk
        print("📝 Generating initial timeline...")
        timeline = await initial_timeline_chain.ainvoke({"context": chunks[0]})
        print(f"✅ Initial timeline generated ({len(timeline)} characters)")
        
        # Iteratively refine with remaining chunks
        for i, chunk in enumerate(chunks[1:], 1):
            print(f"🔄 Refining timeline with chunk {i+1}/{len(chunks)}...")
            
            timeline = await refine_timeline_chain.ainvoke({
                "existing_answer": timeline,
                "context": chunk
            })
            
            print(f"✅ Timeline refined ({len(timeline)} characters)")
        
        return timeline
    
    async def run_timeline_summarization(self):
        """Main method to run the timeline summarization"""
        print("📄 Loading Dota 2 comprehensive document...")
        
        # Load the document content
        content = self.load_dota2_document()
        
        if not content:
            print("❌ Failed to load document content")
            return
        
        print(f"✅ Loaded document ({len(content)} characters)")
        
        # Create document
        document = self.create_documents(content)
        
        # Split into chunks
        chunks = self.split_document_into_chunks(document)
        print(f"📄 Split document into {len(chunks)} chunks")
        
        print("🤖 Generating timeline summary using 'iterative refinement' approach...")
        
        # Generate timeline using iterative refinement
        timeline = await self.iterative_timeline_summarize(chunks)
        
        # Save timeline to file
        with open("dota2_timeline_summary.txt", "w", encoding="utf-8") as f:
            f.write("Dota 2: Comprehensive Timeline Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(timeline)
        
        print("✅ Timeline summary saved to dota2_timeline_summary.txt")
        print("\n📋 Timeline Preview:")
        print("-" * 50)
        print(timeline[:500] + "..." if len(timeline) > 500 else timeline)
        
        return timeline

# Synchronous wrapper for easier execution
def run_timeline_summarization():
    """Synchronous wrapper to run the timeline summarization"""
    summarizer = TimelineSummarization()
    return asyncio.run(summarizer.run_timeline_summarization())

if __name__ == "__main__":
    run_timeline_summarization() 