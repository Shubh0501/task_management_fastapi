from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

# Match the same enums as your Task model
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class UserShort(BaseModel):
    id: UUID
    full_name: str
    email: str

    class Config:
        orm_mode = True

class Subtask(BaseModel):
    id: UUID
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date]

    class Config:
        orm_mode = True

class Dependency(BaseModel):
    id: UUID
    title: str
    status: TaskStatus

    class Config:
        orm_mode = True

# ----- Request Body -----
class TaskCreate(BaseModel):
    title: str = Field(..., example="Task 11001")
    description: Optional[str] = Field(None, example="Create Task Manager application")
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    due_date: Optional[date] = None
    parent_task_id: Optional[UUID] = None

# ----- Response Body -----
class TaskCreateResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    parent_task_id: Optional[UUID]

    class Config:
        orm_mode = True

class TaskSummary(BaseModel):
    id: UUID
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date]

    class Config:
        from_attributes = True

class TaskGet(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    parent_task_id: Optional[UUID]
    subtasks: Optional[List[TaskSummary]] = []
    dependencies: Optional[List[TaskSummary]] = Field(default_factory=list)
    blocked_by: Optional[List[TaskSummary]] = Field(default_factory=list)
    assignees: Optional[List[UserShort]] = []

    class Config:
        orm_mode = True
        from_attributes = True

class TaskUpdate(BaseModel):
    id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    parent_task_id: Optional[UUID] = None
    assignee_ids: Optional[List[UUID]] = None
    depends_on_ids: Optional[List[UUID]] = None
    blocked_by_ids: Optional[List[UUID]] = None

class BulkTaskUpdate(BaseModel):
    tasks: List[TaskUpdate] = []

class TaskUpdateResponse(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    parent_task_id: Optional[UUID] = None
    
    class config:
        orm_mode = True
        from_attributes = True