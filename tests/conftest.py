from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Transaction, TransactionType, User, UserRole
from app.services.auth_service import hash_password


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test_finance.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = testing_session_local()
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
    )
    alice = User(
        username="alice",
        email="alice@example.com",
        hashed_password=hash_password("alice123"),
        role=UserRole.viewer,
    )
    bob = User(
        username="bob",
        email="bob@example.com",
        hashed_password=hash_password("bob123"),
        role=UserRole.analyst,
    )
    db.add_all([admin, alice, bob])
    db.commit()
    db.refresh(admin)
    db.refresh(alice)
    db.refresh(bob)

    db.add_all(
        [
            Transaction(
                owner_id=admin.id,
                amount=5000.0,
                type=TransactionType.income,
                category="Salary",
                date=date(2025, 1, 1),
                notes="Admin salary",
            ),
            Transaction(
                owner_id=admin.id,
                amount=1200.0,
                type=TransactionType.expense,
                category="Rent",
                date=date(2025, 1, 10),
                notes="Admin rent",
            ),
            Transaction(
                owner_id=alice.id,
                amount=3000.0,
                type=TransactionType.income,
                category="Salary",
                date=date(2025, 1, 5),
                notes="Alice salary",
            ),
            Transaction(
                owner_id=alice.id,
                amount=200.0,
                type=TransactionType.expense,
                category="Food",
                date=date(2025, 1, 11),
                notes="Alice groceries",
            ),
            Transaction(
                owner_id=bob.id,
                amount=150.0,
                type=TransactionType.expense,
                category="Transport",
                date=date(2025, 1, 12),
                notes="Bob fuel",
            ),
        ]
    )
    db.commit()
    db.close()

    def override_get_db():
        test_db = testing_session_local()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
