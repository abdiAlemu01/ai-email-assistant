"""Gmail Search Tool"""

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
def search_emails(query: str, limit: int = 5):
    """
    Search emails from Gmail inbox using Gmail search syntax.
    Returns a CONCISE summary of each email to avoid token limits.

    Use this tool when the user asks to:
    - Search for specific emails
    - Find emails with specific criteria
    - Look for emails from a sender
    - Find emails with a specific subject
    - Search for emails with attachments

    Examples:
    - "search for invoices"
    - "find emails from amazon"
    - "search for emails about meeting"
    - "find emails with attachments"
    - "search for emails after July 1st"

    Gmail search syntax examples:
    - invoice
    - from:amazon
    - subject:meeting
    - after:2026/07/01
    - has:attachment
    
    Note: Returns max 5 emails by default to conserve tokens.
    Each email includes: subject, from, date, snippet, and attachment info.
    Full email bodies are truncated to 200 characters.
    """

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
            "note": "Email bodies truncated to 200 chars. Use read_latest_emails for full content if needed."
        }
    
    return results


search_emails_tool = search_emails