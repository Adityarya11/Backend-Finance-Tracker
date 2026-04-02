# Finance Tracker API

A FastAPI backend for managing personal financial records. Supports income and expense tracking, category-level filtering, text search, paginated listing, and role-based access control.

---

## Tech Stack

- **FastAPI** — API framework
- **SQLAlchemy 2** — ORM
- **SQLite** — database (file: `finance.db`)
- **Pydantic v2** — request/response validation
- **python-jose** — JWT token signing
- **passlib + bcrypt** — password hashing

---

## Project Structure

```
finance_tracker/
├── app/
│   ├── main.py                  # App entry point, router registration
│   ├── config.py                # Settings (reads from .env)
│   ├── database.py              # SQLAlchemy engine, session, Base
│   ├── models.py                # ORM models: User, Transaction
│   ├── schemas.py               # Pydantic schemas for all endpoints
│   ├── dependencies.py          # Auth middleware and role guards
│   ├── routers/
│   │   ├── auth.py              # POST /auth/register, /auth/login
│   │   ├── users.py             # GET/PATCH/DELETE /users/
│   │   ├── transactions.py      # CRUD + filter + search /transactions/
│   │   └── summary.py           # GET /summary/
│   └── services/
│       ├── auth_service.py      # JWT encode/decode, password hashing
│       ├── transaction_service.py
│       └── summary_service.py
├── seed.py                      # Populate DB with sample data
├── pyproject.toml
└── .env                         # Optional — override defaults
```

---

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

- API is available at `http://localhost:8000`
- Interactive docs at `http://localhost:8000/docs`

---

## Roles and Permissions

| Action                              | viewer | analyst | admin |
| ----------------------------------- | ------ | ------- | ----- |
| View own transactions               | yes    | yes     | yes   |
| Create transactions                 | yes    | yes     | yes   |
| Update own transactions             | yes    | yes     | yes   |
| Delete transactions                 | no     | no      | yes   |
| View own summary                    | yes    | yes     | yes   |
| Filter and search transactions      | yes    | yes     | yes   |
| View all users' transactions        | no     | no      | yes   |
| View global summary (all users)     | no     | no      | yes   |
| Manage users (list, update, delete) | no     | no      | yes   |

---

## API Overview

### Authentication

```
POST /auth/register    Create a new account
POST /auth/login       Get a Bearer token
POST /auth/token       OAuth2 form token endpoint for Swagger Authorize
```

All other endpoints require the token in the `Authorization: Bearer <token>` header.

## Quick Authorization Guide (Simple)

If you are testing from Swagger (`/docs`), use this flow:

1. Run `seed.py` so demo users exist.
2. Open `/docs` and click **Authorize**.
3. Use these credentials:
   - username: `admin`
   - password: `admin123`
4. Click **Authorize** and **Close**.
5. Call protected endpoints like `GET /users/me` or `GET /transactions/`.

If you are testing with Postman/curl:

1. Call `POST /auth/login` with JSON body:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

2. Copy `access_token` from the response.
3. Send protected requests with header:

```http
Authorization: Bearer <access_token>
```

If you get `401 Unauthorized`, usually one of these is true:

- Token was not added to the request.
- Token expired.
- Wrong `Bearer` format.
- User is inactive.

---

## 5-Minute Recruiter Demo Script

1. Show project structure (`routers`, `services`, `schemas`, `models`) and explain separation of concerns.
2. Login as `admin` and show token-based auth.
3. Call `GET /users/me` to prove protected route authorization.
4. Call `GET /transactions/` with filters (`type`, `category`, `date_from`, `search`, `page`).
5. Call `GET /summary/` and explain computed analytics.
6. Mention RBAC: admin can view all users and delete transactions; non-admin users are scoped to their own data.
7. End with validation examples (`422` for invalid payloads) and test plan.

### Transactions

```
POST   /transactions/            Create a transaction
GET    /transactions/            List transactions (paginated, filterable)
GET    /transactions/{id}        Get a single transaction
PATCH  /transactions/{id}        Update a transaction
DELETE /transactions/{id}        Delete a transaction (admin only)
```

**Query parameters for `GET /transactions/`:**

| Parameter   | Type   | Description                                 |
| ----------- | ------ | ------------------------------------------- |
| `type`      | string | `income` or `expense`                       |
| `category`  | string | Partial match on category name              |
| `date_from` | date   | Start date, format `YYYY-MM-DD` (inclusive) |
| `date_to`   | date   | End date, format `YYYY-MM-DD` (inclusive)   |
| `search`    | string | Searches across category and notes          |
| `page`      | int    | Page number, default `1`                    |
| `page_size` | int    | Results per page, default `20`, max `100`   |

Filters can be combined freely. Admins see all transactions; other roles see only their own.

### Summary

```
GET /summary/    Financial totals, category breakdown, monthly trends, recent activity
```

Admins receive a global summary across all users. Other roles receive their own.

### Users (admin only)

```
GET    /users/        List all users
GET    /users/{id}    Get a user
PATCH  /users/{id}    Update role or active status
DELETE /users/{id}    Delete a user
GET    /users/me      Get your own profile (all roles)
```

---

## Validation

The API returns `422 Unprocessable Entity` for invalid input with a structured error body describing exactly which field failed and why.

Examples of enforced rules:

- `amount` must be greater than zero
- `category` cannot be blank
- `date_from` cannot be after `date_to`
- `email` must be a valid email address
- `username` must be alphanumeric and at least 3 characters
- `password` must be at least 6 characters

---

## Environment Variables

| Variable                      | Default                  | Description               |
| ----------------------------- | ------------------------ | ------------------------- |
| `SECRET_KEY`                  | `dev-secret-key-...`     | JWT signing key           |
| `ALGORITHM`                   | `HS256`                  | JWT algorithm             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                     | Token lifetime in minutes |
| `DATABASE_URL`                | `sqlite:///./finance.db` | SQLAlchemy database URL   |

---

## Assumptions

- Authentication is JWT-based with a Bearer token. No session management.
- SQLite is used for simplicity. The SQLAlchemy setup is compatible with PostgreSQL — changing `DATABASE_URL` is sufficient.
- Admins can create and update transactions on behalf of themselves only via the API; the admin role's privilege is primarily read-all and delete-all access.
- `analyst` and `viewer` roles have identical transaction permissions in the current implementation. The distinction is kept in the model to allow for future differentiation (e.g. restricting export or bulk operations to analysts).
- Amounts are stored as floats and rounded to 2 decimal places at the application layer. A production system would use `DECIMAL(12, 2)` at the database level.
