
from dotenv import load_dotenv
import os
load_dotenv() 

api_key = os.getenv("HUGGINGFACE_API_KEY")
if not api_key:
    raise ValueError(
        "HUGGINGFACE_API_KEY not found in environment variables. "
        "Please set it in your .env file or export it as an environment variable."
    )

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    huggingfacehub_api_token=api_key,
    temperature=0
)

model = ChatHuggingFace(llm=llm)


from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

from ..tools.gmail_reader import read_latest_emails_tool
from ..tools.gmail_search import search_emails


def create_email_agent(model):

    tools = [
        read_latest_emails_tool
    ]

    agent = create_react_agent(
        model=model,
        tools=tools
    )

    return agent




