
# tools/gmail_summarize.py
"""
Gmail Email Summarization Tool

This tool provides AI-powered email summarization with structured output
including key points, action items, and priority classification.
"""

from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

from ..services.gmail_summarize_service import (
    get_email_by_id,
    prepare_email_for_summarization
)


# Define output schema for structured summarization
class EmailSummary(BaseModel):
    """Structured email summary schema."""
    
    summary: str = Field(
        description="A concise 1-2 sentence summary of the email's main message"
    )
    key_points: List[str] = Field(
        description="List of 3-5 key points from the email"
    )
    action_items: List[str] = Field(
        description="List of action items or tasks mentioned in the email"
    )
    important_dates: List[str] = Field(
        description="List of dates, deadlines, or time-sensitive information"
    )
    priority: str = Field(
        description="Email priority level: High, Medium, or Low"
    )
    category: str = Field(
        description="Email category: Work, Personal, Finance, Marketing, meeting,or Other"
    )
    requires_reply: bool = Field(
        description="Whether the email requires a response"
    )

def _create_summarization_prompt() -> ChatPromptTemplate:
    """
    Create the prompt template for email summarization.
    
    Returns:
        ChatPromptTemplate for structured email analysis
    """
    prompt_text = """You are an expert email analyst. Analyze the following email and provide a structured summary.

Email Details:
Subject: {subject}
From: {from_address}
Date: {date}
Body: {body}

Analyze this email and provide:
1. A concise summary (1-2 sentences)
2. Key points (3-5 main points)
3. Action items (tasks or requests mentioned)
4. Important dates (deadlines, meetings, events)
5. Priority level (High/Medium/Low based on urgency and importance)
6. Category (Work/Personal/Finance/Marketing/Other)
7. Whether it requires a reply

{format_instructions}

Provide your analysis in valid JSON format."""
    
    return ChatPromptTemplate.from_template(prompt_text)


@tool
def summarize_email(email_id: str) -> dict:
    """
    Summarize an email by its ID with AI-powered analysis.
    
    Use this tool when the user asks to:
    - Summarize an email
    - Get key points from an email
    - Analyze email content
    - Extract action items from an email
    - Check email priority or category
    
    Args:
        email_id: The Gmail message ID to summarize
        
    Returns:
        Dictionary containing structured summary with:
        - summary: Brief overview
        - key_points: Main points list
        - action_items: Tasks to do
        - important_dates: Time-sensitive info
        - priority: High/Medium/Low
        - category: Email classification
        - requires_reply: Boolean
        
    Examples:
        - "Summarize email abc123"
        - "What are the key points in this email?"
        - "Does this email need a response?"
    """
    try:
        from ..agents.email_agent import model
        
        email_data = get_email_by_id(email_id)
        
        if not email_data:
            return {
                "error": f"Email with ID {email_id} not found",
                "success": False
            }
        
        # Prepare email for summarization
        formatted_email = prepare_email_for_summarization(email_data)
        
        # Create output parser
        parser = JsonOutputParser(pydantic_object=EmailSummary)
        
        # Create prompt
        prompt = _create_summarization_prompt()
        
        # Create the chain
        chain = prompt | model | parser
        
        # Generate summary
        result = chain.invoke({
            "subject": formatted_email["subject"],
            "from_address": formatted_email["from"],
            "date": formatted_email["date"],
            "body": formatted_email["body"],
            "format_instructions": parser.get_format_instructions()
        })
        
        # Add success flag
        result["success"] = True
        result["email_id"] = email_id
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to summarize email: {str(e)}",
            "success": False,
            "email_id": email_id
        }


# Export the tool
summarize_email_tool = summarize_email
