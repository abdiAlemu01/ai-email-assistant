"""    Gmail Search Tool    """

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
    Search Gmail inbox using Gmail search syntax.

    Use this tool when the user wants to find specific emails by criteria like:
    - Keywords (e.g., "AI", "invoice")
    - Sender (e.g., "from:amazon", "from:linkedin")
    - Subject (e.g., "subject:meeting")
    - Attachments (e.g., "has:attachment")
    - Date (e.g., "after:2026/07/01", "newer_than:7d")
    - Status (e.g., "is:unread", "is:starred")

    Args:
        query: Gmail search query string
        limit: Number of emails to return (default: 5, max: 5)

    Returns:
        Concise email summaries with subject, sender, date, snippet, and attachment info.
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