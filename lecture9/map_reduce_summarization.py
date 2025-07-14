import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from bs4 import BeautifulSoup

load_dotenv()

class MapReduceSummarization:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
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
    
    def map_summarize(self, document):
        """Map step: Summarize individual chunks"""
        
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert summarizer. Create a concise summary of the given text chunk about LLM-powered autonomous agents.
            
            Focus on:
            - Key concepts and definitions
            - Important techniques and methods
            - Technical details and architectures
            - Examples and applications
            
            Keep the summary concise but comprehensive."""),
            ("human", "Text chunk to summarize:\n\n{text}")
        ])
        
        map_chain = map_prompt | self.llm | StrOutputParser()
        
        # Split the document into chunks
        chunks = self.text_splitter.split_documents([document])
        
        print(f"📄 Split document into {len(chunks)} chunks")
        
        # Summarize each chunk
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"  Summarizing chunk {i+1}/{len(chunks)}...")
            summary = map_chain.invoke({"text": chunk.page_content})
            summaries.append(summary)
        
        return summaries
    
    def reduce_summarize(self, summaries):
        """Reduce step: Combine all summaries into a final summary"""
        
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert summarizer. Create a comprehensive final summary by combining all the provided summaries about LLM-powered autonomous agents.
            
            Your final summary should include:
            1. Key concepts and definitions
            2. Main architectural components
            3. Important techniques and methods
            4. Real-world applications and examples
            5. Challenges and limitations
            6. Future directions
            
            Organize the information logically and eliminate redundancy. Make the summary clear, well-structured, and informative."""),
            ("human", "Summaries to combine:\n\n{summaries}")
        ])
        
        reduce_chain = reduce_prompt | self.llm | StrOutputParser()
        
        # Combine all summaries
        combined_summaries = "\n\n---\n\n".join(summaries)
        
        print("🔄 Combining summaries into final summary...")
        
        # Generate final summary
        final_summary = reduce_chain.invoke({"summaries": combined_summaries})
        return final_summary
    
    def map_reduce_summarize(self, document):
        """Complete map-reduce summarization process"""
        
        print("🗺️ Starting Map-Reduce summarization...")
        
        # Map step: Summarize chunks
        summaries = self.map_summarize(document)
        
        # Reduce step: Combine summaries
        final_summary = self.reduce_summarize(summaries)
        
        return final_summary
    
    def run_map_reduce_summarization(self):
        """Main method to run the map-reduce summarization"""
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
        
        print("🤖 Generating summary using 'map-reduce' approach...")
        
        # Generate summary using map-reduce
        summary = self.map_reduce_summarize(document)
        
        # Save summary to file
        with open("map_reduce_summary.txt", "w", encoding="utf-8") as f:
            f.write("LLM-Powered Autonomous Agents - Map-Reduce Summarization\n")
            f.write("=" * 60 + "\n\n")
            f.write(summary)
        
        print("✅ Summary saved to map_reduce_summary.txt")
        print("\n📋 Summary Preview:")
        print("-" * 50)
        print(summary[:500] + "..." if len(summary) > 500 else summary)

if __name__ == "__main__":
    summarizer = MapReduceSummarization()
    summarizer.run_map_reduce_summarization() 