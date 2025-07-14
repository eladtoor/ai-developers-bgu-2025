import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from bs4 import BeautifulSoup
from typing import List, Literal, TypedDict
from langchain_core.runnables import RunnableConfig

load_dotenv()

class IterativeRefinementSummarization:
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
        
    def fetch_document_content(self, url):
        """Fetch content from the LLM-powered autonomous agents document"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract the main content
            content = soup.find('article') or soup.find('main') or soup.find('body')
            
            if content:
                # Remove script and style elements
                for script in content(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = content.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text
            else:
                return "Could not extract content from the page."
                
        except Exception as e:
            print(f"Error fetching document: {e}")
            return None
    
    def create_documents(self, content):
        """Create LangChain documents from the content"""
        return Document(
            page_content=content,
            metadata={"source": "https://lilianweng.github.io/posts/2023-06-23-agent/"}
        )
    
    def split_document_into_chunks(self, document):
        """Split the document into smaller chunks for iterative processing"""
        chunks = self.text_splitter.split_documents([document])
        return [chunk.page_content for chunk in chunks]
    
    def create_initial_summary_chain(self):
        """Create the initial summary chain"""
        summarize_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert summarizer. Create a concise but comprehensive initial summary of the given text about LLM-powered autonomous agents.
            
            Focus on:
            - Key concepts and definitions
            - Main architectural components
            - Important techniques and methods
            
            Keep the summary clear and well-structured."""),
            ("human", "Write a concise summary of the following: {context}")
        ])
        
        return summarize_prompt | self.llm | StrOutputParser()
    
    def create_refine_summary_chain(self):
        """Create the refinement chain"""
        refine_template = """
        You are an expert summarizer. Refine the existing summary with new information.
        
        Existing summary up to this point:
        {existing_answer}
        
        New context:
        ------------
        {context}
        ------------
        
        Given the new context, refine the original summary. Add new information, clarify existing points, and ensure the summary remains comprehensive and well-structured.
        
        Focus on:
        - Key concepts and definitions
        - Main architectural components  
        - Important techniques and methods
        - Real-world applications and examples
        - Challenges and limitations
        - Future directions
        """
        
        refine_prompt = ChatPromptTemplate.from_messages([
            ("human", refine_template)
        ])
        
        return refine_prompt | self.llm | StrOutputParser()
    
    async def iterative_refinement_summarize(self, chunks):
        """Perform iterative refinement summarization"""
        
        if not chunks:
            return "No content to summarize."
        
        print(f"🔄 Starting iterative refinement with {len(chunks)} chunks...")
        
        # Create chains
        initial_summary_chain = self.create_initial_summary_chain()
        refine_summary_chain = self.create_refine_summary_chain()
        
        # Generate initial summary from first chunk
        print("📝 Generating initial summary...")
        summary = await initial_summary_chain.ainvoke({"context": chunks[0]})
        print(f"✅ Initial summary generated ({len(summary)} characters)")
        
        # Iteratively refine with remaining chunks
        for i, chunk in enumerate(chunks[1:], 1):
            print(f"🔄 Refining summary with chunk {i+1}/{len(chunks)}...")
            
            summary = await refine_summary_chain.ainvoke({
                "existing_answer": summary,
                "context": chunk
            })
            
            print(f"✅ Summary refined ({len(summary)} characters)")
        
        return summary
    
    async def run_iterative_refinement_summarization(self):
        """Main method to run the iterative refinement summarization"""
        print("📄 Fetching LLM-powered autonomous agents document...")
        
        # Fetch the document content
        url = "https://lilianweng.github.io/posts/2023-06-23-agent/"
        content = self.fetch_document_content(url)
        
        if not content:
            print("❌ Failed to fetch document content")
            return
        
        print(f"✅ Fetched document ({len(content)} characters)")
        
        # Create document
        document = self.create_documents(content)
        
        # Split into chunks
        chunks = self.split_document_into_chunks(document)
        print(f"📄 Split document into {len(chunks)} chunks")
        
        print("🤖 Generating summary using 'iterative refinement' approach...")
        
        # Generate summary using iterative refinement
        summary = await self.iterative_refinement_summarize(chunks)
        
        # Save summary to file
        with open("iterative_refinement_summary.txt", "w", encoding="utf-8") as f:
            f.write("LLM-Powered Autonomous Agents - Iterative Refinement Summarization\n")
            f.write("=" * 60 + "\n\n")
            f.write(summary)
        
        print("✅ Summary saved to iterative_refinement_summary.txt")
        print("\n📋 Summary Preview:")
        print("-" * 50)
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return summary

# Synchronous wrapper for easier execution
def run_iterative_refinement():
    """Synchronous wrapper to run the iterative refinement summarization"""
    summarizer = IterativeRefinementSummarization()
    return asyncio.run(summarizer.run_iterative_refinement_summarization())

if __name__ == "__main__":
    run_iterative_refinement() 