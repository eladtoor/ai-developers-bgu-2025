from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from timeline_prompts import create_extract_timeline_prompt, create_improve_timeline_prompt

def refine_timeline_function(file_path: str) -> str:
    """
    Create a timeline summary using Refine method.
    
    Args:
        file_path: Path to the text file to summarize
        
    Returns:
        A refined timeline summary with bullet points
    """
    # Load the document
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    
    # Initialize the language model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Create improve timeline chain
    improve_chain = PromptTemplate(
        input_variables=["existing_summary", "text"],
        template=create_improve_timeline_prompt()
    ) | llm | StrOutputParser()
    
    # Start with the first chunk as the initial timeline
    current_timeline = create_extract_timeline_prompt().format(text=chunks[0])
    current_timeline = llm.invoke(current_timeline)
    
    # Improve with each subsequent chunk
    for chunk in chunks[1:]:
        current_timeline = improve_chain.invoke({
            "existing_summary": current_timeline,
            "text": chunk
        })
    
    return current_timeline 