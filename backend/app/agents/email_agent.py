
from dotenv import load_dotenv
import os
load_dotenv() 

from langchain_groq import ChatGroq

model = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)


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


