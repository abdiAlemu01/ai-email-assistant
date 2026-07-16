


# api/routes/review.py
"""
Review API Routes

Endpoints for managing email review requests (human-in-the-loop approval).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ...services.human_review_service import get_review_service
from ...services.gmail_send_service import send_email_direct, send_draft_by_id


router = APIRouter(prefix="/review", tags=["review"])


class ApprovalRequest(BaseModel):
    """Request model for approving an email."""
    review_id: str


class RejectionRequest(BaseModel):
    """Request model for rejecting an email."""
    review_id: str
    reason: Optional[str] = None


@router.get("/pending")
async def get_pending_reviews():
    """
    Get all pending email review requests.
    
    Returns:
        List of pending reviews awaiting approval
    """
    try:
        review_service = get_review_service()
        pending = review_service.get_pending_reviews()
        
        return {
            "success": True,
            "count": len(pending),
            "reviews": pending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_reviews(status: Optional[str] = None):
    """
    Get all review requests, optionally filtered by status.
    
    Args:
        status: Optional status filter (pending, approved, rejected, sent)
    
    Returns:
        List of all reviews
    """
    try:
        review_service = get_review_service()
        reviews = review_service.get_all_reviews(status=status)
        
        return {
            "success": True,
            "count": len(reviews),
            "status_filter": status,
            "reviews": reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}")
async def get_review(review_id: str):
    """
    Get a specific review request by ID.
    
    Args:
        review_id: Review request ID
    
    Returns:
        Review details
    """
    try:
        review_service = get_review_service()
        review = review_service.get_review(review_id)
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "success": True,
            "review": review
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_review(request: ApprovalRequest):
    """
    Approve a review request and send the email.
    
    Args:
        request: Approval request with review_id
    
    Returns:
        Approval result and email send status
    """
    try:
        review_service = get_review_service()
        
        # Get review
        review = review_service.get_review(request.review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if already processed
        if review["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Review already {review['status']}"
            )
        
        # Approve the review
        approved = review_service.approve_review(request.review_id)
        if not approved:
            raise HTTPException(status_code=500, detail="Failed to approve review")
        
        # Send the email
        email_data = review["email_data"]
        draft_id = email_data.get("draft_id")
        
        if draft_id:
            # Send from draft
            result = send_draft_by_id(draft_id)
        else:
            # Send direct email
            result = send_email_direct(
                to=email_data["to"],
                subject=email_data["subject"],
                body=email_data["body"],
                thread_id=email_data.get("thread_id"),
                in_reply_to=email_data.get("in_reply_to"),
                references=email_data.get("references")
            )
        
        if result.get("success"):
            # Mark as sent
            review_service.mark_as_sent(
                request.review_id,
                result.get("message_id", "")
            )
            
            return {
                "success": True,
                "status": "sent",
                "review_id": request.review_id,
                "message_id": result.get("message_id"),
                "message": "Email approved and sent successfully"
            }
        else:
            return {
                "success": False,
                "status": "send_failed",
                "review_id": request.review_id,
                "error": result.get("error", "Unknown error"),
                "message": "Email was approved but failed to send"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject")
async def reject_review(request: RejectionRequest):
    """
    Reject a review request.
    
    Args:
        request: Rejection request with review_id and optional reason
    
    Returns:
        Rejection confirmation
    """
    try:
        review_service = get_review_service()
        
        # Get review
        review = review_service.get_review(request.review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if already processed
        if review["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Review already {review['status']}"
            )
        
        # Reject the review
        rejected = review_service.reject_review(request.review_id, request.reason)
        if not rejected:
            raise HTTPException(status_code=500, detail="Failed to reject review")
        
        return {
            "success": True,
            "status": "rejected",
            "review_id": request.review_id,
            "reason": request.reason,
            "message": "Email review rejected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}")
async def delete_review(review_id: str):
    """
    Delete a review request.
    
    Args:
        review_id: Review request ID
    
    Returns:
        Deletion confirmation
    """
    try:
        review_service = get_review_service()
        
        deleted = review_service.delete_review(review_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "success": True,
            "review_id": review_id,
            "message": "Review deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_reviews(days: int = 7):
    """
    Clean up old review requests.
    
    Args:
        days: Number of days to keep (default: 7)
    
    Returns:
        Cleanup results
    """
    try:
        review_service = get_review_service()
        deleted_count = review_service.cleanup_old_reviews(days=days)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} old reviews"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
