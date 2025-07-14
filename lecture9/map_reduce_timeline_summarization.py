import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class MapReduceTimelineSummarization:
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
    
    def map_timeline_extract(self, document):
        """Map step: Extract timeline information from individual chunks"""
        
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert timeline analyst. Extract timeline information from the given text chunk about Dota 2 history.
            
            Focus on:
            - Exact dates and years mentioned
            - Major events, releases, tournaments, and patches
            - Hero releases and item introductions
            - Technical innovations and platform developments
            - Tournament dates and prize pools
            
            Extract all timeline-relevant information from this chunk."""),
            ("human", "Extract timeline information from this text chunk:\n\n{text}")
        ])
        
        map_chain = map_prompt | self.llm | StrOutputParser()
        
        # Split the document into chunks
        chunks = self.text_splitter.split_documents([document])
        
        print(f"📄 Split document into {len(chunks)} chunks")
        
        # Extract timeline info from each chunk
        timeline_extracts = []
        for i, chunk in enumerate(chunks):
            print(f"  Extracting timeline from chunk {i+1}/{len(chunks)}...")
            extract = map_chain.invoke({"text": chunk.page_content})
            timeline_extracts.append(extract)
        
        return timeline_extracts
    
    def reduce_timeline_combine(self, timeline_extracts):
        """Reduce step: Combine all timeline extracts into a final timeline"""
        
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert timeline analyst. Create a comprehensive, chronological timeline by combining all the provided timeline extracts about Dota 2 history.
            
            Your final timeline should:
            1. Include all dates and events from all extracts
            2. Be organized chronologically
            3. Remove duplicates and consolidate similar events
            4. Provide clear, accurate timeline information
            5. Include major milestones, releases, tournaments, and innovations
            
            Create a well-structured timeline with specific dates and events."""),
            ("human", "Timeline extracts to combine:\n\n{extracts}")
        ])
        
        reduce_chain = reduce_prompt | self.llm | StrOutputParser()
        
        # Combine all timeline extracts
        combined_extracts = "\n\n---\n\n".join(timeline_extracts)
        
        print("🔄 Combining timeline extracts into final timeline...")
        
        # Generate final timeline
        final_timeline = reduce_chain.invoke({"extracts": combined_extracts})
        return final_timeline
    
    def map_reduce_timeline_summarize(self, document):
        """Complete map-reduce timeline summarization process"""
        
        print("🗺️ Starting Map-Reduce timeline extraction...")
        
        # Map step: Extract timeline info from chunks
        timeline_extracts = self.map_timeline_extract(document)
        
        # Reduce step: Combine extracts into final timeline
        final_timeline = self.reduce_timeline_combine(timeline_extracts)
        
        return final_timeline
    
    def run_map_reduce_timeline_summarization(self):
        """Main method to run the map-reduce timeline summarization"""
        print("📄 Loading Dota 2 comprehensive document...")
        
        # Load the document content
        content = self.load_dota2_document()
        
        if not content:
            print("❌ Failed to load document content")
            return
        
        print(f"✅ Loaded document ({len(content)} characters)")
        
        # Create document
        document = self.create_documents(content)
        
        print("🤖 Generating timeline using 'map-reduce' approach...")
        
        # Generate timeline using map-reduce
        timeline = self.map_reduce_timeline_summarize(document)
        
        # Save timeline to file
        with open("map_reduce_timeline_summary.txt", "w", encoding="utf-8") as f:
            f.write("Dota 2: Map-Reduce Approach Timeline Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(timeline)
        
        print("✅ Timeline summary saved to map_reduce_timeline_summary.txt")
        print("\n📋 Timeline Preview:")
        print("-" * 50)
        print(timeline[:500] + "..." if len(timeline) > 500 else timeline)
        
        return timeline

if __name__ == "__main__":
    summarizer = MapReduceTimelineSummarization()
    summarizer.run_map_reduce_timeline_summarization() 