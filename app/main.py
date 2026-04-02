from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, users, transactions, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Finance Tracker API",
    description=(
        "A backend system for managing personal financial records. "
        "Supports income/expense tracking, category-level analytics, monthly summaries, "
        "and role-based access control.\n\n"
        "**Roles**\n"
        "- `viewer` / `analyst`: manage their own transactions, view their own summary\n"
        "- `admin`: full access to all transactions, global summary, and user management\n\n"
        "Authenticate via `/auth/login` and pass the returned token as a Bearer header."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(summary.router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "message": "Finance Tracker API is running"}