# Finance Tracker API Documentation

This document is the official API reference for the Finance Tracker backend.

---

## 1. Project Overview

Finance Tracker is a FastAPI backend for personal finance management with:

- JWT authentication
- Role-based access control (viewer, analyst, admin)
- Transaction CRUD with filtering, search, and pagination
- Analytics summary (totals, category breakdown, monthly trends, recent activity)

### Tech Stack

- FastAPI
- SQLAlchemy 2
- SQLite (default)
- Pydantic v2
- python-jose (JWT)
- passlib + bcrypt (password hashing)

### Code Architecture

- `app/main.py`: app bootstrap, metadata, and router registration
- `app/routers/`: route handlers (`auth`, `users`, `transactions`, `summary`)
- `app/services/`: business logic and data processing
- `app/schemas.py`: request/response models and validation rules
- `app/models.py`: SQLAlchemy ORM models and enums
- `app/dependencies.py`: token validation and role-based guards
- `seed.py`: deterministic seed users and sample transactions

---

## 2. Base URLs and API Docs Endpoints

### Local Development

- Base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### Health Endpoint

- `GET /`

Response:

```json
{
  "status": "ok",
  "message": "Finance Tracker API is running"
}
```

---

## 3. Local Setup and Run

### Prerequisites

- Python 3.11+

### Install dependencies

```bash
pip install -r requirements.txt
```

### (Optional) Configure environment

Create `.env` in project root if you want custom settings:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./finance.db
```

### Seed sample data

```bash
python seed.py
```

Seeded users:

- `admin / admin123` (admin)
- `alice / alice123` (viewer)
- `bob / bob123` (analyst)

### Run API server

```bash
uvicorn app.main:app --reload
```

---

## 4. Authentication and Authorization

All protected endpoints require a JWT token in:

`Authorization: Bearer <token>`

### Auth Endpoints

#### `POST /auth/register`

Register a new user.

Request body:

```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "secret123",
  "role": "viewer"
}
```

Response (`201 Created`):

```json
{
  "id": 4,
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "viewer",
  "is_active": true
}
```

#### `POST /auth/login`

Login with JSON credentials.

Request body:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response (`200 OK`):

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

#### `POST /auth/token`

OAuth2 Password Grant endpoint used by Swagger Authorize.

Content type: `application/x-www-form-urlencoded`

Form fields:

- `username`
- `password`

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Role Access Matrix

| Action                            | viewer    | analyst   | admin  |
| --------------------------------- | --------- | --------- | ------ |
| Get own profile (`GET /users/me`) | yes       | yes       | yes    |
| List users (`GET /users/`)        | no        | no        | yes    |
| Update/delete users               | no        | no        | yes    |
| Create transaction                | yes       | yes       | yes    |
| View own transactions             | yes       | yes       | yes    |
| View all users' transactions      | no        | no        | yes    |
| Update own transaction            | yes       | yes       | yes    |
| Delete transaction                | no        | no        | yes    |
| Get summary                       | own scope | own scope | global |

---

## 5. Data Models

### User

- `id` (int)
- `username` (alphanumeric, min length 3)
- `email` (valid email)
- `role` (`viewer` | `analyst` | `admin`)
- `is_active` (bool)

### Transaction

- `id` (int)
- `amount` (float, must be > 0)
- `type` (`income` | `expense`)
- `category` (non-empty string)
- `date` (YYYY-MM-DD)
- `notes` (optional string)
- `owner_id` (int)

### Summary Response

- `total_income` (float)
- `total_expenses` (float)
- `current_balance` (float)
- `transaction_count` (int)
- `category_breakdown` (list)
- `monthly_totals` (list)
- `recent_transactions` (list, max 5)

---

## 6. Endpoint Reference

### 6.1 Users

#### `GET /users/me`

Returns the authenticated user profile.

#### `GET /users/` (admin only)

Returns all users sorted by id.

#### `GET /users/{user_id}` (admin only)

Returns a specific user by id.

#### `PATCH /users/{user_id}` (admin only)

Updates user role or active status.

Request body example:

```json
{
  "role": "analyst",
  "is_active": true
}
```

#### `DELETE /users/{user_id}` (admin only)

Deletes a user (admin cannot delete own account).

---

### 6.2 Transactions

#### `POST /transactions/`

Create a transaction for the authenticated user.

Request body:

```json
{
  "amount": 99.5,
  "type": "expense",
  "category": "Food",
  "date": "2025-02-01",
  "notes": "Dinner"
}
```

Response (`201 Created`):

```json
{
  "id": 21,
  "amount": 99.5,
  "type": "expense",
  "category": "Food",
  "date": "2025-02-01",
  "notes": "Dinner",
  "owner_id": 2
}
```

#### `GET /transactions/`

List transactions with filters and pagination.

Query parameters:

- `type`: `income` or `expense`
- `category`: partial match (case-insensitive)
- `date_from`: start date (inclusive)
- `date_to`: end date (inclusive)
- `search`: searches category and notes
- `page`: default `1`, min `1`
- `page_size`: default `20`, min `1`, max `100`

Example:

`GET /transactions/?type=expense&category=food&page=1&page_size=10`

Response shape:

```json
{
  "total": 3,
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "id": 7,
      "amount": 80.0,
      "type": "expense",
      "category": "Food",
      "date": "2025-02-20",
      "notes": "Groceries",
      "owner_id": 1
    }
  ]
}
```

#### `GET /transactions/{tx_id}`

Returns one transaction. Non-admin users can only access their own transactions.

#### `PATCH /transactions/{tx_id}`

Partially updates a transaction.

Request body example:

```json
{
  "notes": "Updated note"
}
```

#### `DELETE /transactions/{tx_id}` (admin only)

Deletes a transaction.

---

### 6.3 Summary

#### `GET /summary/`

Returns:

- income and expense totals
- current balance
- category breakdown (sum + count)
- monthly totals (income, expenses, balance)
- recent transactions (latest 5)

Admin receives global summary (all users).
Viewer/Analyst receive user-scoped summary.

---

## 7. Validation and Error Handling

Common status codes:

- `200 OK`: success
- `201 Created`: resource created
- `204 No Content`: deletion success
- `400 Bad Request`: logical validation failed (example: invalid date range)
- `401 Unauthorized`: missing/invalid token or invalid login
- `403 Forbidden`: role not permitted or account deactivated
- `404 Not Found`: resource does not exist
- `422 Unprocessable Entity`: schema validation error

Example `422` response:

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0",
      "input": 0
    }
  ]
}
```

---

## 8. Business Logic Notes

- Transactions are owner-scoped for non-admin users.
- Search is implemented with case-insensitive partial matching on category and notes.
- Summary calculations use SQL aggregations and are rounded to 2 decimal places.
- Monthly summary is grouped by year and month and split by transaction type.

---

## 9. Testing

Automated tests are available in `tests/test_api_phase1.py`.

Run tests:

```bash
python -m pytest -q
```

Current test coverage includes:

- authentication success/failure
- unauthorized access behavior
- role-based route protection
- transaction CRUD and filtering
- summary scoping (admin vs regular user)
- validation paths for invalid payload and date ranges

---
