from datetime import date as dt_date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import UserRole, TransactionType


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, pattern=r"^[A-Za-z0-9]+$")
    email: EmailStr
    role: UserRole = UserRole.viewer


    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip()

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    type: TransactionType
    category: str = Field(..., min_length=1)
    date: dt_date
    notes: Optional[str] = None


    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("category cannot be blank")
        return cleaned

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[dt_date] = None
    notes: Optional[str] = None


    @field_validator("category")
    @classmethod
    def validate_optional_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("category cannot be blank")
        return cleaned

class TransactionResponse(TransactionBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class PaginatedTransactions(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[TransactionResponse]


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int


class MonthlyTotal(BaseModel):
    year: int
    month: int
    income: float
    expenses: float
    balance: float

class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    current_balance: float
    transaction_count: int
    category_breakdown: list[CategoryBreakdown]
    monthly_totals: list[MonthlyTotal]
    recent_transactions: list[TransactionResponse]
