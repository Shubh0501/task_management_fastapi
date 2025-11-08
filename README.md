# 🧩 Task Management API (FastAPI + PostgreSQL)

A fully asynchronous **Task Management System** built on **FastAPI** and **PostgreSQL**.

Key features:

- 🔐 JWT authentication + refresh tokens (30 Minutes validity of access tokens)
- 🧑‍🤝‍🧑 Role-based Access Control (RBAC)
- ✅ Task creation, editing, dependencies, subtasks, assignees
- 📊 Analytics API (showing task distribution + overdue tasks + unassigned tasks)
- ⚡ Async DB with Alembic migrations
- 🧠 Modular architecture for scalability

---

## 🏗️ Architecture Overview

| Layer            | Technology                                           |
| ---------------- | ---------------------------------------------------- |
| Web Framework    | **FastAPI**                                          |
| ORM              | **SQLModel** (on SQLAlchemy 2.x)                     |
| Database         | **PostgreSQL**                                       |
| Migrations       | **Alembic**                                          |
| Auth             | **JWT tokens** (access + refresh)                    |
| Password Hashing | **bcrypt**                                           |
| Middleware       | Custom `AuthenticationMiddleware` for JWT validation |
| Containerization | Ready for Docker / Kubernetes (optional)             |

---

---

## ⚙️ Setup & Initialization

### ① Install Dependencies

```bash
git clone https://github.com/Shubh0501/task_management_fastapi.git
cd task_management_fastapi
python3 -m venv tm_venv
source ./tm_venv/bin/activate
pip install -r requirements.txt
```

### ② Update Environment Variables

**Under /src/config.py File, update the following keys**

```bash
DB_URL=postgresql://uname:pass@localhost:5432/task_db
DB_ASYNC_URL=postgresql+asyncpg://uname:pass@localhost:5432/task_db
DB_NAME=task_db
JWT_SECRET_KEY="supersecretkey"
```

### ③ Initialise the Database

\*_After creating the database with given name / other name such as task_db_

```bash
alembic upgrade head
```

### ③ Start the Server

**Run the command in your terminal to start the application**

```bash
uvicorn src.main:app --reload
```

### ④ Run the Startup Endpoint (First time only)

**Run this cURL in another terminal window / Using Postman**

```bash
curl --location 'http://localhost:8000/run-startup-script'
```

### ⑤ Access the Swagger Docs

**Access the Docs of the APIs using these links to get more information**

```bash
Main DOCS: http://localhost:8000/docs
Authentication DOCS: http://localhost:8000/auth/docs
Task Management DOCS: http://localhost:8000/task/docs
```

## Usage Guidelines

> Once the project is up and running, use /auth/register route to create an user, and /auth/login to generate Access token and Refresh Tokens. Once logged in, use the access token as the bearer token to authorise the requests for task creation and updating. Use /task/create route to create new tasks, /task/update to update single/multiple tasks as once, /task/analytics/get-task-distribution to get the task distribution and status update for all users.

## Product Features choosen

### ① Making tasks dependent on other tasks

> Allowing tasks to depend on other tasks makes the system more realistic and useful for real project workflows. It ensures that work progresses in the correct order — a task can’t be completed until its prerequisites are done. This prevents mistakes, clarifies what is blocking progress, and helps teams plan better. Dependencies also make it easier to track bottlenecks, coordinate efforts, and maintain accountability. Overall, it turns a simple task list into a structured workflow system that reflects how real teams operate, improving visibility, accuracy, and collaboration across projects.

### ② Analytics for Task distribution and overdue tasks / user

> An API that shows task distribution and overdue tasks per user adds clear visibility and measurable accountability to a task management system. It helps identify how work is spread across the team, highlighting imbalances or overloading early. Tracking overdue tasks ensures that deadlines are not missed unnoticed and that project progress remains transparent. This data-driven view enables managers to prioritize resources, reassign tasks, and make informed decisions quickly. Overall, it transforms raw task data into actionable insights, improving efficiency, workload management, and team productivity through simple, real-time analytics.
