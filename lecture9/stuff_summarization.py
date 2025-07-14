import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
import requests
from bs4 import BeautifulSoup

load_dotenv()

class StuffSummarization:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    def fetch_document_content(self, url):
        """Fetch content from the LLM-powered autonomous agents document"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract the main content (adjust selectors based on the actual page structure)
            # For Lilian Weng's blog, the content is typically in article tags
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
    
    def create_document(self, content):
        """Create a LangChain document from the content"""
        return Document(
            page_content=content,
            metadata={"source": "https://lilianweng.github.io/posts/2023-06-23-agent/"}
        )
    
    def stuff_summarize(self, document):
        """Summarize using the 'stuff' approach - put everything in one prompt"""
        
        # Create the summarization prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert summarizer. Create a comprehensive summary of the given document about LLM-powered autonomous agents.
            
            Your summary should include:
            1. Key concepts and definitions
            2. Main architectural components
            3. Important techniques and methods
            4. Real-world applications and examples
            5. Challenges and limitations
            6. Future directions
            
            Make the summary clear, well-structured, and informative. Use bullet points where appropriate."""),
            ("human", "Document to summarize:\n\n{document}")
        ])
        
        # Create the chain
        chain = prompt | self.llm | StrOutputParser()
        
        # Generate summary
        summary = chain.invoke({"document": document.page_content})
        return summary
    
    def run_stuff_summarization(self):
        """Main method to run the stuff summarization"""
        print("📄 Fetching LLM-powered autonomous agents document...")
        
        # Fetch the document content
        url = "https://lilianweng.github.io/posts/2023-06-23-agent/"
        content = self.fetch_document_content(url)
        
        if not content:
            print("❌ Failed to fetch document content")
            return
        
        print(f"✅ Fetched document ({len(content)} characters)")
        
        # Create document
        document = self.create_document(content)
        
        print("🤖 Generating summary using 'stuff' approach...")
        
        # Generate summary
        summary = self.stuff_summarize(document)
        
        # Save summary to file
        with open("stuff_summary.txt", "w", encoding="utf-8") as f:
            f.write("LLM-Powered Autonomous Agents - Stuff Summarization\n")
            f.write("=" * 60 + "\n\n")
            f.write(summary)
        
        print("✅ Summary saved to stuff_summary.txt")
        print("\n📋 Summary Preview:")
        print("-" * 50)
        print(summary[:500] + "..." if len(summary) > 500 else summary)

if __name__ == "__main__":
    summarizer = StuffSummarization()
    summarizer.run_stuff_summarization() 