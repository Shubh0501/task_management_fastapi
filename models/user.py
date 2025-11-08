import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from models.role import UserRoleLink #noqa: E402
import sqlalchemy as sa

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    full_name: str
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False))

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    tasks_created: List["Task"] = Relationship(back_populates="creator")
    assigned_tasks: List["TaskAssignee"] = Relationship(back_populates="user")