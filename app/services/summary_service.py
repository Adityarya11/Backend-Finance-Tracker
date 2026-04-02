from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Transaction, TransactionType
from app.schemas import (
    CategoryBreakdown,
    MonthlyTotal,
    SummaryResponse,
    TransactionResponse,
)


def get_summary(db: Session, user_id: int | None = None) -> SummaryResponse:
    base_q = db.query(Transaction)
    if user_id is not None:
        base_q = base_q.filter(Transaction.owner_id == user_id)

    income: float = (
        base_q.filter(Transaction.type == TransactionType.income)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0.0))
        .scalar()
    )

    expenses: float = (
        base_q.filter(Transaction.type == TransactionType.expense)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0.0))
        .scalar()
    )

    count: int = base_q.count()

    # Per-category totals across all transaction types
    category_rows = (
        base_q.with_entities(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("tx_count"),
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    category_breakdown = [
        CategoryBreakdown(
            category=row.category,
            total=round(float(row.total), 2),
            count=int(row.tx_count),
        )
        for row in category_rows
    ]

    # Monthly breakdown split by transaction type
    monthly_q = db.query(
        extract("year", Transaction.date).label("year"),
        extract("month", Transaction.date).label("month"),
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
    )
    if user_id is not None:
        monthly_q = monthly_q.filter(Transaction.owner_id == user_id)

    monthly_rows = (
        monthly_q
        .group_by("year", "month", Transaction.type)
        .order_by("year", "month")
        .all()
    )

    monthly_map: dict[tuple[int, int], dict[str, float]] = {}
    for row in monthly_rows:
        key = (int(row.year), int(row.month))
        if key not in monthly_map:
            monthly_map[key] = {"income": 0.0, "expenses": 0.0}
        if row.type == TransactionType.income:
            monthly_map[key]["income"] += float(row.total)
        else:
            monthly_map[key]["expenses"] += float(row.total)

    monthly_totals = [
        MonthlyTotal(
            year=year,
            month=month,
            income=round(vals["income"], 2),
            expenses=round(vals["expenses"], 2),
            balance=round(vals["income"] - vals["expenses"], 2),
        )
        for (year, month), vals in sorted(monthly_map.items())
    ]

    recent = (
        base_q.order_by(Transaction.date.desc()).limit(5).all()
    )

    return SummaryResponse(
        total_income=round(float(income), 2),
        total_expenses=round(float(expenses), 2),
        current_balance=round(float(income) - float(expenses), 2),
        transaction_count=count,
        category_breakdown=category_breakdown,
        monthly_totals=monthly_totals,
        recent_transactions=[TransactionResponse.model_validate(t) for t in recent],
    )