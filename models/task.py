import uuid
import enum
from datetime import datetime, date, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from models.user import User
import sqlalchemy as sa

class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

# ----------------- LINK TABLES -----------------

class TaskAssignee(SQLModel, table=True):
    task_id: uuid.UUID = Field(default=None, foreign_key="task.id", primary_key=True)
    user_id: uuid.UUID = Field(default=None, foreign_key="user.id", primary_key=True)
    is_owner: bool = Field(default=False)

    task: Optional["Task"] = Relationship(back_populates="assignees")
    user: Optional["User"] = Relationship(back_populates="assigned_tasks")


class TaskDependency(SQLModel, table=True):
    task_id: uuid.UUID = Field(default=None, foreign_key="task.id", primary_key=True)
    depends_on_task_id: uuid.UUID = Field(default=None, foreign_key="task.id", primary_key=True)

    task: Optional["Task"] = Relationship(
        back_populates="dependencies", sa_relationship_kwargs={"foreign_keys": "[TaskDependency.task_id]"}
    )
    depends_on: Optional["Task"] = Relationship(
        back_populates="blocked_by", sa_relationship_kwargs={"foreign_keys": "[TaskDependency.depends_on_task_id]"}
    )

# ----------------- MAIN TABLE -----------------

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    due_date: Optional[date] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc)))

    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    parent_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="task.id")

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="tasks_created")
    subtasks: List["Task"] = Relationship(back_populates="parent", sa_relationship_kwargs={"cascade": "all, delete"})
    parent: Optional["Task"] = Relationship(back_populates="subtasks", sa_relationship_kwargs={"remote_side": "Task.id"})
    assignees: List["TaskAssignee"] = Relationship(back_populates="task")
    dependencies: List["TaskDependency"] = Relationship(back_populates="task",         sa_relationship_kwargs={"foreign_keys": "TaskDependency.task_id"})
    blocked_by: List["TaskDependency"] = Relationship(back_populates="depends_on", sa_relationship_kwargs={"foreign_keys": "TaskDependency.depends_on_task_id"})