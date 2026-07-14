
from dotenv import load_dotenv
import os
load_dotenv() 

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in environment variables. "
        "Please set it in your .env file or export it as an environment variable."
    )

from langchain_groq import ChatGroq

# Initialize Groq model
model = ChatGroq(
    model="llama-3.3-70b-versatile",  # Fast and powerful
    api_key=api_key,
    temperature=0
)


from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

from ..tools.gmail_reader import read_latest_emails_tool
from ..tools.gmail_search import search_emails_tool
from ..tools.gmail_summarize import summarize_email_tool
from ..tools.gmail_draft_replies import draft_replies_email_tool


def create_email_agent(model):

    tools = [
        read_latest_emails_tool,
        search_emails_tool,
        summarize_email_tool
    ]

    agent = create_react_agent(
        model=model,
        tools=tools
    )

    return agent




