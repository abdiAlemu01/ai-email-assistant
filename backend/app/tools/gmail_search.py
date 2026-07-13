"""Gmail Search Tool"""

from langchain.tools import tool

from ..services import gmail_search_service


@tool
def search_emails(query: str):
    """
    Search emails from Gmail inbox.

    Examples:
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