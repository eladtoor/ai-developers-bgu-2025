import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document

load_dotenv()

class StuffTimelineSummarization:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
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
    
    def create_document(self, content):
        """Create a LangChain document from the content"""
        return Document(
            page_content=content,
            metadata={"source": "dota2_comprehensive_document.txt"}
        )
    
    def stuff_timeline_summarize(self, document):
        """Summarize using the 'stuff' approach - put everything in one prompt"""
        
        # Create the timeline extraction prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert timeline analyst. Extract and create a comprehensive timeline from the given document about Dota 2 history.
            
            Your timeline should include:
            1. All exact dates and years mentioned in the document
            2. Major events, releases, tournaments, and patches
            3. Chronological order of events
            4. Key milestones and developments
            5. Hero releases and item introductions
            6. Tournament dates and prize pools
            7. Technical innovations and platform developments
            
            Create a clear, chronological timeline with specific dates. Format as a timeline with years and events."""),
            ("human", "Document to extract timeline from:\n\n{document}")
        ])
        
        # Create the chain
        chain = prompt | self.llm | StrOutputParser()
        
        # Generate timeline
        timeline = chain.invoke({"document": document.page_content})
        return timeline
    
    def run_stuff_timeline_summarization(self):
        """Main method to run the stuff timeline summarization"""
        print("📄 Loading Dota 2 comprehensive document...")
        
        # Load the document content
        content = self.load_dota2_document()
        
        if not content:
            print("❌ Failed to load document content")
            return
        
        print(f"✅ Loaded document ({len(content)} characters)")
        
        # Create document
        document = self.create_document(content)
        
        print("🤖 Generating timeline using 'stuff' approach...")
        
        # Generate timeline
        timeline = self.stuff_timeline_summarize(document)
        
        # Save timeline to file
        with open("stuff_timeline_summary.txt", "w", encoding="utf-8") as f:
            f.write("Dota 2: Stuff Approach Timeline Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(timeline)
        
        print("✅ Timeline summary saved to stuff_timeline_summary.txt")
        print("\n📋 Timeline Preview:")
        print("-" * 50)
        print(timeline[:500] + "..." if len(timeline) > 500 else timeline)
        
        return timeline

if __name__ == "__main__":
    summarizer = StuffTimelineSummarization()
    summarizer.run_stuff_timeline_summarization() 