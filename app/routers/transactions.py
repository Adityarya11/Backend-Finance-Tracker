from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, TransactionType
from app.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    PaginatedTransactions,
)
from app.dependencies import get_current_user, require_roles
from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
    delete_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
)
def create(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_transaction(db, data, current_user.id)


@router.get(
    "/",
    response_model=PaginatedTransactions,
    summary="List transactions with optional filters and search",
)
def list_all(
    tx_type: Optional[TransactionType] = Query(None, alias="type", description="Filter by income or expense"),
    category: Optional[str] = Query(None, description="Filter by category name (partial match)"),
    date_from: Optional[date] = Query(None, description="Start date (inclusive), format: YYYY-MM-DD"),
    date_to: Optional[date] = Query(None, description="End date (inclusive), format: YYYY-MM-DD"),
    search: Optional[str] = Query(None, description="Search across category and notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from cannot be after date_to")

    # Admins see all transactions; everyone else sees only their own
    scoped_user_id = None if current_user.role == UserRole.admin else current_user.id

    results, total = list_transactions(
        db,
        user_id=scoped_user_id,
        tx_type=tx_type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedTransactions(
        total=total,
        page=page,
        page_size=page_size,
        results=[TransactionResponse.model_validate(tx) for tx in results],
    )


@router.get(
    "/{tx_id}",
    response_model=TransactionResponse,
    summary="Get a single transaction by ID",
)
def get_one(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_user_id = None if current_user.role == UserRole.admin else current_user.id
    tx = get_transaction(db, tx_id, scoped_user_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.patch(
    "/{tx_id}",
    response_model=TransactionResponse,
    summary="Update a transaction",
)
def update(
    tx_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_user_id = None if current_user.role == UserRole.admin else current_user.id
    tx = get_transaction(db, tx_id, scoped_user_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return update_transaction(db, tx, data)


@router.delete(
    "/{tx_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction (admin only)",
)
def delete(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    delete_transaction(db, tx)