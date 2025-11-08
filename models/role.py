import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import enum

class RoleList(str, enum.Enum):
    TASK_CREATE = "TASK_CREATE"
    TASK_EDIT = "TASK_EDIT"
    TASK_DELETE = "TASK_DELETE"
    TASK_VIEW = "TASK_VIEW"

class UserRoleLink(SQLModel, table=True):
    user_id: uuid.UUID = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: uuid.UUID = Field(default=None, foreign_key="role.id", primary_key=True)
    is_active: bool = Field(default=True)

class Role(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    description: Optional[str] = None
    code: Optional[RoleList] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)