"""Gmail Search Tool"""

from langchain.tools import tool

from ..services import gmail_search_service


@tool
def search_emails(query: str):
    """
    Search emails from Gmail inbox using Gmail search syntax.

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
    """

    results = gmail_search_service.search_emails(
        query=query,
        limit=10
    )

    return results


search_emails_tool = search_emails