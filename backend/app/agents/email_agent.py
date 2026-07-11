
from dotenv import load_dotenv
import os
load_dotenv() 

from langchain_huggingface import ChatHuggingFace
from langchain_community.llms import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
    temperature=0
)

model = ChatHuggingFace(llm=llm)


from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

from ..tools.gmail_reader import read_latest_emails_tool


def create_email_agent(model):

    tools = [
        read_latest_emails_tool
    ]

    agent = create_react_agent(
        model=model,
        tools=tools
    )

    return agent


