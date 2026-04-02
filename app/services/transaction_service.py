from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Transaction, TransactionType
from app.schemas import TransactionCreate, TransactionUpdate


def create_transaction(db: Session, data: TransactionCreate, user_id: int) -> Transaction:
    tx = Transaction(**data.model_dump(), owner_id=user_id)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transaction(
    db: Session, tx_id: int, user_id: int | None = None
) -> Transaction | None:
    q = db.query(Transaction).filter(Transaction.id == tx_id)
    if user_id is not None:
        q = q.filter(Transaction.owner_id == user_id)
    return q.first()


def list_transactions(
    db: Session,
    user_id: int | None = None,
    tx_type: TransactionType | None = None,
    category: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Transaction], int]:
    q = db.query(Transaction)

    if user_id is not None:
        q = q.filter(Transaction.owner_id == user_id)
    if tx_type is not None:
        q = q.filter(Transaction.type == tx_type)
    if category:
        q = q.filter(Transaction.category.ilike(f"%{category}%"))
    if date_from:
        q = q.filter(Transaction.date >= date_from)
    if date_to:
        q = q.filter(Transaction.date <= date_to)
    if search:
        q = q.filter(
            or_(
                Transaction.category.ilike(f"%{search}%"),
                Transaction.notes.ilike(f"%{search}%"),
            )
        )

    total = q.count()
    results = (
        q.order_by(Transaction.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return results, total


def update_transaction(
    db: Session, tx: Transaction, data: TransactionUpdate
) -> Transaction:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, tx: Transaction) -> None:
    db.delete(tx)
    db.commit()