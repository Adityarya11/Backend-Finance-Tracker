"""
This script is for the seeding the data to the db.
"""

from datetime import date
from app.database import engine, SessionLocal, Base
from app import models
from app.models import User, UserRole, Transaction, TransactionType
from app.services.auth_service import hash_password


def main():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    transactions = [
        # Admin
        Transaction(owner_id=admin.id, amount=5000.00, type=TransactionType.income,  category="Salary",      date=date(2025, 1,  1), notes="January salary"),
        Transaction(owner_id=admin.id, amount=1200.00, type=TransactionType.expense, category="Rent",        date=date(2025, 1, 10), notes="Monthly rent"),
        Transaction(owner_id=admin.id, amount=200.00,  type=TransactionType.expense, category="Food",        date=date(2025, 1, 15), notes="Groceries"),
        Transaction(owner_id=admin.id, amount=5000.00, type=TransactionType.income,  category="Salary",      date=date(2025, 2,  1), notes="February salary"),
        Transaction(owner_id=admin.id, amount=500.00,  type=TransactionType.income,  category="Freelance",   date=date(2025, 2, 10), notes="Side project payment"),
        Transaction(owner_id=admin.id, amount=150.00,  type=TransactionType.expense, category="Utilities",   date=date(2025, 2, 14), notes="Electricity bill"),
        Transaction(owner_id=admin.id, amount=80.00,   type=TransactionType.expense, category="Transport",   date=date(2025, 2, 20), notes="Monthly bus pass"),
        Transaction(owner_id=admin.id, amount=5000.00, type=TransactionType.income,  category="Salary",      date=date(2025, 3,  1), notes="March salary"),
        Transaction(owner_id=admin.id, amount=1200.00, type=TransactionType.expense, category="Rent",        date=date(2025, 3, 10), notes="Monthly rent"),
        Transaction(owner_id=admin.id, amount=300.00,  type=TransactionType.expense, category="Shopping",    date=date(2025, 3, 18), notes="Clothes"),
        # Alice
        Transaction(owner_id=alice.id, amount=3500.00, type=TransactionType.income,  category="Salary",      date=date(2025, 1,  5), notes="January salary"),
        Transaction(owner_id=alice.id, amount=900.00,  type=TransactionType.expense, category="Rent",        date=date(2025, 1, 10), notes="Rent payment"),
        Transaction(owner_id=alice.id, amount=120.00,  type=TransactionType.expense, category="Food",        date=date(2025, 1, 22), notes="Weekly groceries"),
        Transaction(owner_id=alice.id, amount=3500.00, type=TransactionType.income,  category="Salary",      date=date(2025, 2,  5), notes="February salary"),
        Transaction(owner_id=alice.id, amount=200.00,  type=TransactionType.income,  category="Freelance",   date=date(2025, 2, 18), notes="Design work"),
        # Bob
        Transaction(owner_id=bob.id,   amount=4200.00, type=TransactionType.income,  category="Salary",      date=date(2025, 1,  3), notes="January salary"),
        Transaction(owner_id=bob.id,   amount=1000.00, type=TransactionType.expense, category="Rent",        date=date(2025, 1,  8), notes="Rent"),
        Transaction(owner_id=bob.id,   amount=60.00,   type=TransactionType.expense, category="Transport",   date=date(2025, 1, 25), notes="Fuel"),
        Transaction(owner_id=bob.id,   amount=4200.00, type=TransactionType.income,  category="Salary",      date=date(2025, 2,  3), notes="February salary"),
        Transaction(owner_id=bob.id,   amount=350.00,  type=TransactionType.expense, category="Shopping",    date=date(2025, 2, 27), notes="Electronics"),
    ]
    db.add_all(transactions)
    db.commit()
    db.close()

    print("Database seeded successfully.")
    print()
    print("Credentials")
    print("-----------")
    print("  admin  / admin123  (role: admin)")
    print("  alice  / alice123  (role: viewer)")
    print("  bob    / bob123    (role: analyst)")


if __name__ == "__main__":
    main()