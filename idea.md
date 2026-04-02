# Python Finance Tracking Backend

## 1. Overview

This project is a **Python-based Finance Tracking Backend System** designed to help users manage and analyze their financial records.

The goal is to build a **clean, simple, and well-structured backend** that demonstrates:

- Strong Python fundamentals
- Clear API design
- Logical business handling
- Maintainable architecture

This implementation prioritizes **clarity, correctness, and clean code** over unnecessary complexity, as emphasized in the assignment .

---

## Assessment Status (Current)

### What is already implemented

- JWT-based authentication (`/auth/login`, `/auth/token`)
- Role-based route protection (viewer / analyst / admin)
- Transaction CRUD with filtering, search, and pagination
- Summary analytics (income, expenses, balance, category split, monthly totals, recent transactions)
- User management endpoints (`/users`, `/users/{id}`, `/users/me`)
- Input validation using Pydantic v2
- Seed script with realistic mock users and transactions

### What to prioritize next

1. Automated tests for auth, permissions, and core endpoints
2. Edge-case validation tests (`422`, `400`, `403`, `404`)
3. Optional enhancements (export, advanced search, richer analytics)

---

## 2. Tech Stack

- **Backend Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Server:** Uvicorn

### Why this stack?

- FastAPI provides clean and modern API design
- SQLite keeps setup simple and lightweight
- SQLAlchemy ensures structured database interaction
- Pydantic enforces strong input validation

---

## 3. Core Features

### 3.1 Financial Records Management

The system supports full CRUD operations for financial transactions.

Each record includes:

- `id`
- `amount`
- `type` (income / expense)
- `category`
- `date`
- `notes`

#### Supported Operations:

- Create a record
- Retrieve all records
- Retrieve filtered records
- Update a record
- Delete a record

#### Filtering Support:

- By date range
- By category
- By transaction type

---

### 3.2 Summary & Analytics

The backend provides computed financial insights:

- Total Income
- Total Expenses
- Current Balance
- Category-wise breakdown
- Monthly summaries
- Recent transactions

These are implemented as **service-layer functions**, separating logic from routes.

---

### 3.3 User & Role Handling

Basic role-based behavior is implemented:

| Role    | Permissions              |
| ------- | ------------------------ |
| Viewer  | View records & summaries |
| Analyst | View + filter + insights |
| Admin   | Full CRUD access         |

> Note: Authentication is kept minimal (or mocked) to focus on backend design clarity.

---

### 3.4 API Design

The system exposes RESTful APIs using FastAPI.

#### Example Routes:

**Transactions**

- `POST /transactions`
- `GET /transactions`
- `GET /transactions/{id}`
- `PUT /transactions/{id}`
- `DELETE /transactions/{id}`

**Filters**

- `GET /transactions?type=income`
- `GET /transactions?category=food`
- `GET /transactions?start_date=&end_date=`

**Analytics**

- `GET /summary`
- `GET /summary/monthly`
- `GET /summary/category`

**Users (Basic)**

- `GET /users`
- `POST /users`

---

### 3.5 Validation & Error Handling

Handled using **Pydantic schemas and FastAPI validation**.

Includes:

- Type validation (amount must be numeric)
- Required fields enforcement
- Proper HTTP status codes
- Meaningful error messages

Example:

- `400 Bad Request` for invalid input
- `404 Not Found` for missing records

---

### 3.6 Database Design

Using SQLite with SQLAlchemy ORM.

#### Tables:

**Users**

- id
- name
- role

**Transactions**

- id
- amount
- type
- category
- date
- notes
- user_id (optional)

Design focuses on:

- Simplicity
- Logical relationships
- Easy querying

---

### Design Philosophy:

- Separation of concerns
- Business logic isolated from routes
- Clean modular structure

---

## 4. Business Logic Approach

- All calculations (totals, summaries) handled in **service layer**
- Routes only handle:
  - Request parsing
  - Response formatting

This ensures:

- Reusability
- Testability
- Clean architecture

---

## 5. Assumptions

- Users are pre-created or handled minimally
- Authentication is simplified or skipped
- Single-user usage is acceptable for MVP
- Data size is small (SQLite sufficient)

---

## 6. Optional Enhancements (If Time Permits)

- JWT Authentication
- Pagination (`limit`, `offset`)
- CSV export
- Search functionality
- Unit tests

---

## 7. Key Focus Areas

This project emphasizes:

- Clean Python code
- Logical backend design
- Proper API structuring
- Robust validation
- Maintainability

A simple, well-built system is intentionally preferred over a complex one.

---

## 8. Outcome

The final system will be:

- Easy to understand
- Easy to extend
- Functionally correct
- Structured like a real-world backend

It can directly serve as a backend for a finance dashboard or application.

---
