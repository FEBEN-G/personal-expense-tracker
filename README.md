# Personal Expense Tracker API

A Django REST Framework API for tracking personal expenses with user authentication and category management.

## Features

- User Registration & Authentication (Token-based)
- CRUD operations for Categories
- CRUD operations for Expenses  
- Filter expenses by category and date range
- Expense summary with total calculations
- User-specific data isolation
- Admin interface for data management

## Tech Stack

- **Backend**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (Development)
- **Authentication**: Token Authentication
- **CORS**: django-cors-headers

## VS Code Setup

1. Open the project in VS Code
2. Open the workspace file: `personal-expense-tracker.code-workspace`
3. Install recommended extensions when prompted
4. Open integrated terminal (Ctrl + \`)
5. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
