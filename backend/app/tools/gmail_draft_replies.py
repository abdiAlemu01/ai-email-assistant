# tools/gmail_draft_replies.py
"""
Gmail Draft Reply Tool

This tool provides AI-powered draft reply generation with context-aware
responses based on the original email content.
"""

from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional

from ..services.gmail_draft_replies_service import (
    prepare_reply_metadata,
    create_draft_in_gmail,
    format_reply_body,
    get_user_email_address
)
from ..services.gmail_summarize_service import (
    get_email_by_id,
    prepare_email_for_summarization
)


# Define output schema for draft reply
class DraftReply(BaseModel):
    """Structured draft reply schema."""
    
    greeting: str = Field(
        description="Personalized greeting with recipient's name"
    )
    acknowledgment: str = Field(
        description="Acknowledgment of the original email content"
    )
    main_response: str = Field(
        description="Main response addressing the email content"
    )
    closing: str = Field(
        description="Professional closing statement"
    )
    tone: str = Field(
        description="Tone of the reply: Professional, Friendly, or Formal"
    )



def _create_reply_prompt() -> ChatPromptTemplate:
    """
    Create the prompt template for draft reply generation.
    
    Returns:
        ChatPromptTemplate for context-aware reply generation
    """
    prompt_text = """You are an expert email reply assistant.
     Generate a professional, context-aware draft reply to the following email.

Original Email:
Subject: {subject}
From: {from_name} ({from_address})
Date: {date}
Body: {body}

Instructions:
1. Create a personalized greeting using the sender's name: {from_name}
2. Acknowledge the content of their email
3. Provide a thoughtful, relevant response based on the email content
4. Use a professional and courteous tone
5. Keep the response concise but complete
6. Add a professional closing

Important:
- Address the sender by their first name
- Show you understood their message
- Be helpful and constructive
- Match the tone of the original email (if formal, be formal; 
if friendly, be warm but professional)

{format_instructions}

Provide your draft reply in valid JSON format."""
    
    return ChatPromptTemplate.from_template(prompt_text)


def _format_full_reply(draft_parts: dict, user_name: str) -> str:
    """
    Format the draft reply parts into a complete email body.
    
    Args:
        draft_parts: Dictionary with greeting, acknowledgment,
         main_response, closing
        user_name: Name of the user for signature
        
    Returns:
        Complete formatted email body
    """
    parts = [
        draft_parts.get("greeting", ""),
        "",  # Blank line after greeting
        draft_parts.get("acknowledgment", ""),
        "",  # Blank line
        draft_parts.get("main_response", ""),
        "",  # Blank line
        draft_parts.get("closing", ""),
        "",  # Blank line before signature
        f"Best regards,",
        user_name
    ]
    
    return "\n".join(parts)


@tool
def draft_reply_email(email_id: str, custom_instructions: Optional[str] = None) -> dict:
    """
    Generate and create a draft reply for an email.
    
    Use this tool when the user asks to:
    - Draft a reply to an email
    - Create a response to an email
    - Reply to a message
    - Generate an email response
    
    Args:
        email_id: The Gmail message ID to reply to
        custom_instructions: Optional custom instructions for the reply content
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if draft was created
        - draft_id: Gmail draft ID
        - preview: Preview of the generated reply
        - to: Recipient email
        - subject: Reply subject
        
    Examples:
        - "Draft a reply to email abc123"
        - "Create a response to this email"
        - "Reply to the latest email from John"
    """
    try:
        from ..agents.email_agent import model
        
        # Get original email
        email_data = get_email_by_id(email_id)
        
        if not email_data:
            return {
                "error": f"Email with ID {email_id} not found",
                "success": False
            }
        
        # Prepare email content
        formatted_email = prepare_email_for_summarization(email_data)
        
        # Prepare reply metadata
        reply_meta = prepare_reply_metadata(email_data)
        
        # Get user info for signature
        user_email = get_user_email_address()
        user_name = user_email.split("@")[0].replace(".", " ").title() if user_email else "User"
        
        # Create output parser
        parser = JsonOutputParser(pydantic_object=DraftReply)
        
        # Create prompt
        prompt = _create_reply_prompt()
        
        # Add custom instructions to body if provided
        email_body = formatted_email["body"]
        if custom_instructions:
            email_body += f"\n\n[CUSTOM INSTRUCTIONS: {custom_instructions}]"
        
        # Create the chain
        chain = prompt | model | parser
        
        # Generate draft reply
        draft_parts = chain.invoke({
            "subject": formatted_email["subject"],
            "from_name": reply_meta["sender_name"],
            "from_address": reply_meta["to"],
            "date": formatted_email["date"],
            "body": email_body,
            "format_instructions": parser.get_format_instructions()
        })
        
        # Format complete reply body
        reply_body = _format_full_reply(draft_parts, user_name)
        
        # Create draft in Gmail
        draft_result = create_draft_in_gmail(
            to=reply_meta["to"],
            subject=reply_meta["subject"],
            body=reply_body,
            thread_id=reply_meta["thread_id"],
            in_reply_to=reply_meta["in_reply_to"],
            references=reply_meta["references"]
        )
        
        if draft_result.get("success"):
            return {
                "success": True,
                "draft_id": draft_result["draft_id"],
                "message_id": draft_result["message_id"],
                "thread_id": draft_result["thread_id"],
                "to": reply_meta["to"],
                "subject": reply_meta["subject"],
                "preview": reply_body[:200] + "..." if len(reply_body) > 200 else reply_body,
                "tone": draft_parts.get("tone", "Professional"),
                "message": f"Draft reply created successfully for email from {reply_meta['sender_name']}"
            }
        else:
            return {
                "success": False,
                "error": draft_result.get("error", "Failed to create draft"),
                "email_id": email_id
            }
        
    except Exception as e:
        return {
            "error": f"Failed to draft reply: {str(e)}",
            "success": False,
            "email_id": email_id
        }


# Export the tool
draft_replies_email_tool = draft_reply_email
