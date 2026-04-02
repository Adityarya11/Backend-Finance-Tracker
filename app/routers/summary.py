from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.schemas import SummaryResponse
from app.dependencies import get_current_user
from app.services.summary_service import get_summary

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get(
    "/",
    response_model=SummaryResponse,
    summary="Get financial summary and analytics",
    description=(
        "Returns totals, per-category breakdown, monthly trends, and recent activity. "
        "Admins receive a global summary across all users. "
        "All other roles receive a summary scoped to their own transactions."
    ),
)
def financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_user_id = None if current_user.role == UserRole.admin else current_user.id
    return get_summary(db, user_id=scoped_user_id)