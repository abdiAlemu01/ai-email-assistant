"""    Gmail Search Tool    """

from typing import Union
from langchain.tools import tool

from ..services import gmail_search_service


def format_email_summary(email):
    """Format email data into a concise summary for AI processing."""
    # Truncate body to first 200 characters
    body = email.get("body", "")
    if len(body) > 200:
        body = body[:200] + "..."
    
    # Get attachment names only
    attachments = [att.get("filename", "unknown") for att in email.get("attachments", [])]
    
    # Create concise summary
    summary = {
        "id": email.get("id", ""),
        "subject": email.get("subject", "No subject"),
        "from": email.get("from", "Unknown"),
        "date": email.get("date", "Unknown date"),
        "snippet": email.get("snippet", "")[:150],  # First 150 chars of snippet
        "has_attachments": len(attachments) > 0,
        "attachment_names": attachments[:3] if attachments else [],  # Max 3 attachment names
        "is_read": email.get("isRead", True),
        "is_starred": email.get("isStarred", False)
    }
    
    return summary


@tool
def search_emails(query: str, limit: Union[str, int] = 5):
    """
    Search the user's Gmail inbox using Gmail search syntax and return concise email summaries.

    Use this tool whenever the user wants to search, find, filter, or locate emails that match
    specific criteria instead of simply reading the latest emails.

    Use this tool for requests such as:
    - Search my emails
    - Find emails
    - Look for emails
    - Search for invoices
    - Find emails from Amazon
    - Show emails from LinkedIn
    - Find emails from GitHub
    - Search emails from Udemy
    - Find emails from a specific sender
    - Search by subject
    - Search by keyword
    - Find emails with attachments
    - Show unread emails
    - Find starred emails
    - Search emails from today
    - Search emails from yesterday
    - Find emails from this week
    - Search emails after a specific date
    - Search emails before a specific date

    Examples of user requests:
    - "Find invoices"
    - "Search emails about AI"
    - "Show emails from Amazon"
    - "Find LinkedIn emails from today"
    - "Search unread emails"
    - "Find emails with attachments"
    - "Search emails after July 1st"
    - "Show emails before January 2026"

    Convert the user's request into the appropriate Gmail search query.

    Examples:
    - invoice
    - AI
    - from:amazon
    - from:linkedin
    - from:github
    - from:udemy
    - subject:meeting
    - has:attachment
    - is:unread
    - is:starred
    - newer_than:7d
    - newer_than:1d
    - after:2026/07/01
    - before:2026/07/31

    Args:
        query (str):
            Gmail search query.

        limit (int):
            Maximum number of emails to return.
            Must be an INTEGER, never a string.
            Default: 5
            Maximum: 5

    Returns:
        A concise list of matching emails containing:
        - Subject
        - Sender
        - Date
        - Snippet
        - Read/Unread status
        - Attachment information

    Notes:
    - Always use an INTEGER for `limit` (e.g. 5, not "5").
    - Return at most 5 emails to reduce token usage.
    - Email bodies are truncated to keep responses efficient.
    - If no emails match, return an empty result instead of generating an answer.
    """

    # Handle string input from LLM (LLMs sometimes pass numbers as strings in JSON)
    if isinstance(limit, str):
        limit = int(limit)

    # Limit to 5 emails by default to avoid token limits
    results = gmail_search_service.search_emails(
        query=query,
        limit=min(limit, 5)  # Cap at 5 emails
    )

    # Convert to concise summaries
    if isinstance(results, list):
        summaries = [format_email_summary(email) for email in results]
        return {
            "count": len(summaries),    
            "emails": summaries,
            "note": "Email bodies truncated to 200 chars. Use read_emails for full content if needed."
        }


    return results

search_emails_tool = search_emails