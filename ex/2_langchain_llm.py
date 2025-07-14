from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

load_dotenv()

# Create an OpenAI chat model instance
chat_llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create a prompt with a simple system rule and a dynamic user prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that always responds in a friendly and informative way."),
    ("human", "{user_input}")
])

# Chain the prompt, model, and string output parser
rhyme_chain = prompt | chat_llm | StrOutputParser()

# Run the chain with a sample input
result = rhyme_chain.invoke({"user_input": "Hello, how are you?"})  

print(result)
