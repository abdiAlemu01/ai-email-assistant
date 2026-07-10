
from dotenv import load_dotenv
import os
load_dotenv() 

from langchain.tools import tool

from langchain.agents import create_agent

from ..tools.gmail_reader import read_latest_emails_tool


def create_email_agent(model):

    tools = [
        read_latest_emails_tool
    ]


    agent = create_agent(
        model=model,
        tools=tools
    )


    return agent


