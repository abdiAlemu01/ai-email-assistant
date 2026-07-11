from dotenv import load_dotenv
import os
load_dotenv()

from app.agents.email_agent import create_email_agent, model

# Create the agent
agent = create_email_agent(model)

# Test with natural language
test_queries = [
    "Read the first 5 emails from my inbox",
    "Show me my latest emails",
    "I want to see my recent messages"
]

print("Testing AI Email Agent with natural language queries...\n")

for query in test_queries:
    print(f"Query: {query}")
    print("-" * 50)
    try:
        response = agent.invoke({"messages": [("human", query)]})
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n" + "="*50 + "\n")
