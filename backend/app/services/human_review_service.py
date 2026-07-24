"""
Human Review Service

This service manages human-in-the-loop approval for email sending.
Stores pending emails awaiting approval and tracks approval status.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json
from pathlib import Path

class HumanReviewService:
    """
    Service for managing email approvals with human-in-the-loop.
    
    In production, this would use a database. For now, using in-memory storage
    with optional file persistence.
    """
    
    def __init__(self, persist_to_file: bool = True):
        """
        Initialize the review service.
        
        Args:
            persist_to_file: Whether to persist pending reviews to file
        """
        self.pending_reviews: Dict[str, Dict[str, Any]] = {}
        self.persist_to_file = persist_to_file
        self.storage_file = Path(__file__).parent.parent.parent / "pending_reviews.json"
        
        # Load existing reviews if file exists
        if self.persist_to_file and self.storage_file.exists():
            self._load_from_file()
    
    def create_review_request(
        self,
        to: str,
        subject: str,
        body: str,
        draft_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new review request for email approval.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            draft_id: Optional draft ID if email is from draft
            thread_id: Optional thread ID for replies
            in_reply_to: Optional In-Reply-To header
            references: Optional References header
            metadata: Additional metadata
            
        Returns:
            Review ID (UUID)
        """
        review_id = str(uuid.uuid4())
        
        review_data = {
            "review_id": review_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "email_data": {
                "to": to,
                "subject": subject,
                "body": body,
                "draft_id": draft_id,
                "thread_id": thread_id,
                "in_reply_to": in_reply_to,
                "references": references
            },
            "metadata": metadata or {},
            "approved_at": None,
            "rejected_at": None,
            "rejection_reason": None
        }
        
        self.pending_reviews[review_id] = review_data
        
        if self.persist_to_file:
            self._save_to_file()
        
        return review_id
    
    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a review request by ID.
        
        Args:
            review_id: Review request ID
            
        Returns:
            Review data or None if not found
        """
        return self.pending_reviews.get(review_id)
    
    def approve_review(self, review_id: str) -> bool:
        """
        Approve a review request.
        
        Args:
            review_id: Review request ID
            
        Returns:
            True if approved, False if review not found
        """
        review = self.pending_reviews.get(review_id)
        if not review:
            return False
        
        review["status"] = "approved"
        review["approved_at"] = datetime.now().isoformat()
        
        if self.persist_to_file:
            self._save_to_file()
        
        return True
    
    def reject_review(self, review_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject a review request.
        
        Args:
            review_id: Review request ID
            reason: Optional rejection reason
            
        Returns:
            True if rejected, False if review not found
        """
        review = self.pending_reviews.get(review_id)
        if not review:
            return False
        
        review["status"] = "rejected"
        review["rejected_at"] = datetime.now().isoformat()
        review["rejection_reason"] = reason
        
        if self.persist_to_file:
            self._save_to_file()
        
        return True
    
    def mark_as_sent(self, review_id: str, message_id: str) -> bool:
        """
        Mark a review as sent after successful email sending.
        
        Args:
            review_id: Review request ID
            message_id: Gmail message ID of sent email
            
        Returns:
            True if marked, False if review not found
        """
        review = self.pending_reviews.get(review_id)
        if not review:
            return False
        
        review["status"] = "sent"
        review["sent_at"] = datetime.now().isoformat()
        review["message_id"] = message_id
        
        if self.persist_to_file:
            self._save_to_file()
        
        return True
    
    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """
        Get all pending review requests.
        
        Returns:
            List of pending reviews
        """
        return [
            review for review in self.pending_reviews.values()
            if review["status"] == "pending"
        ]
    
    def get_all_reviews(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all review requests, optionally filtered by status.
        
        Args:
            status: Optional status filter (pending, approved, rejected, sent)
            
        Returns:
            List of reviews
        """
        reviews = list(self.pending_reviews.values())
        
        if status:
            reviews = [r for r in reviews if r["status"] == status]
        
        # Sort by creation time, newest first
        reviews.sort(key=lambda x: x["created_at"], reverse=True)
        
        return reviews
    
    def edit_review(
        self,
        review_id: str,
        to: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None
    ) -> bool:
        """
        Edit a pending review request's email data.
        
        Only pending reviews can be edited. Once approved or rejected,
        the email cannot be modified.
        
        Args:
            review_id: Review request ID
            to: New recipient email (optional)
            subject: New email subject (optional)
            body: New email body (optional)
            
        Returns:
            True if edited, False if review not found or not pending
        """
        review = self.pending_reviews.get(review_id)
        if not review:
            return False
        
        # Only allow editing pending reviews
        if review["status"] != "pending":
            return False
        
        # Update provided fields
        if to is not None:
            review["email_data"]["to"] = to
        if subject is not None:
            review["email_data"]["subject"] = subject
        if body is not None:
            review["email_data"]["body"] = body
        
        # Update edited timestamp
        review["edited_at"] = datetime.now().isoformat()
        
        if self.persist_to_file:
            self._save_to_file()
        
        return True
    
    def delete_review(self, review_id: str) -> bool:
        """
        Delete a review request.
        
        Args:
            review_id: Review request ID
            
        Returns:
            True if deleted, False if not found
        """
        if review_id in self.pending_reviews:
            del self.pending_reviews[review_id]
            
            if self.persist_to_file:
                self._save_to_file()
            
            return True
        
        return False
    
    def cleanup_old_reviews(self, days: int = 7) -> int:
        """
        Clean up reviews older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of reviews deleted
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_delete = []
        for review_id, review in self.pending_reviews.items():
            created_at = datetime.fromisoformat(review["created_at"])
            if created_at < cutoff_date and review["status"] in ["sent", "rejected"]:
                to_delete.append(review_id)
        
        for review_id in to_delete:
            del self.pending_reviews[review_id]
        
        if to_delete and self.persist_to_file:
            self._save_to_file()
        
        return len(to_delete)
    
    def _save_to_file(self):
        """Save pending reviews to file."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.pending_reviews, f, indent=2)
        except Exception as e:
            print(f"Error saving reviews to file: {str(e)}")
    
    def _load_from_file(self):
        """Load pending reviews from file."""
        try:
            with open(self.storage_file, "r") as f:
                self.pending_reviews = json.load(f)
        except Exception as e:
            print(f"Error loading reviews from file: {str(e)}")
            self.pending_reviews = {}


# Global instance for the application
_review_service = None


def get_review_service() -> HumanReviewService:
    """
    Get the global review service instance.
    
    Returns:
        HumanReviewService instance
    """
    global _review_service
    if _review_service is None:
        _review_service = HumanReviewService(persist_to_file=True)
    return _review_service
