from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import select, delete, func
from src.database import get_db_session
from models.task import Task, TaskAssignee, TaskDependency, TaskStatus
from .structure import TaskCreate, TaskGet, TaskCreateResponse, TaskSummary, UserShort, TaskUpdate, BulkTaskUpdate
from models.role import RoleList
from models.user import User
from uuid import UUID
from src.utils.checkaccessservice import check_access
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from .service import update_task_object

router = APIRouter(tags=["Tasks"])

@router.post("/create", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
@check_access(RoleList.TASK_CREATE.value)
async def create_task(
    task_in: TaskCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    # Create a new task linked to the logged-in user
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        parent_task_id=task_in.parent_task_id,
        created_by=request.user.id
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskGet)
@check_access(RoleList.TASK_VIEW.value)
async def get_task_details(
    task_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Checking for authorization
    if task.created_by != request.user.id:
        assigned = (await session.execute(
            select(TaskAssignee).where(
                (TaskAssignee.task_id == task.id) &
                (TaskAssignee.user_id == request.user.id)
            )
        )).scalars().first()
        if not assigned:
            raise HTTPException(status_code=403, detail="Not authorized to view this task")

    # Getting all subtasks related to the task
    subtasks = (await session.execute(select(Task).where(Task.parent_task_id == task.id))).scalars().all()

    # Getting all task dependencies
    depends_on = (
        await session.execute(
    select(Task)
    .join(TaskDependency, Task.id == TaskDependency.depends_on_task_id)
    .where(TaskDependency.task_id == task.id)
)
    ).scalars().all()

    # Getting list of tasks that this task is blocked by
    blocked_by = (
        await session.execute(
    select(Task)
    .join(TaskDependency, Task.id == TaskDependency.task_id)
    .where(TaskDependency.depends_on_task_id == task.id)
)
    ).scalars().all()

    # Getting list of all the assignees
    assignees = (
        await session.execute(
    select(User)
    .join(TaskAssignee, User.id == TaskAssignee.user_id)
    .where(TaskAssignee.task_id == task.id)
)
    ).scalars().all()

    # Final response
    task_data = TaskGet(**task.__dict__)
    task_data.subtasks = [TaskSummary.model_validate(t, from_attributes=True) for t in subtasks]
    task_data.dependencies = [TaskSummary.model_validate(t, from_attributes=True) for t in depends_on]
    task_data.blocked_by = [TaskSummary.model_validate(t, from_attributes=True) for t in blocked_by]
    task_data.assignees = [UserShort.model_validate(u, from_attributes=True) for u in assignees]
    return task_data

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@check_access(RoleList.TASK_DELETE.value)
async def delete_task(
    task_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.created_by != request.user.id:
        result = await session.execute(
            select(TaskAssignee).where(
                (TaskAssignee.task_id == task.id) &
                (TaskAssignee.user_id == request.user.id)
            )
        )
        assigned = result.scalars().first()
        if not assigned:
            raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    result = await session.execute(
        select(Task).where(Task.parent_task_id == task.id)
    )
    subtasks = result.scalars().all()

    if subtasks:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete task with existing subtasks. Please delete them first."
        )

    # Cleaning up dependencies & assignee links
    await session.execute(
        delete(TaskDependency).where(
            (TaskDependency.task_id == task.id)
            | (TaskDependency.depends_on_task_id == task.id)
        )
    )
    await session.execute(
        delete(TaskAssignee).where(TaskAssignee.task_id == task.id)
    )

    await session.delete(task)
    await session.commit()

    return {"message": "Task deleted successfully"}

@router.put("/update")
@check_access(RoleList.TASK_EDIT.value)
async def update_task(
    task_data: TaskUpdate | BulkTaskUpdate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    if hasattr(task_data, "tasks"):
        for task in task_data.tasks:
            await update_task_object(inc_task=task, user=request.user, session=session)
    else:
        await update_task_object(inc_task=task_data, user=request.user, session=session)
    
    await session.commit()
    return "Tasks Updated successfully"

@router.get("/analytics/get-task-distribution")
@check_access(RoleList.TASK_VIEW.value)
async def get_task_analytics(
    request: Request, #noqa
    session: AsyncSession = Depends(get_db_session),
):
    now = datetime.now(timezone.utc)
    task_dist = (await session.execute(
        select(
            User.id,
            User.full_name,
            func.count(TaskAssignee.task_id).label("assigned_tasks")
        )
        .join(TaskAssignee, User.id == TaskAssignee.user_id)
        .group_by(User.id)
    )).all()
    task_distribution = [
        {"user_id": id, "user_name": full_name, "assigned_tasks": count}
        for id, full_name, count in task_dist
    ]

    status_data = (await session.execute(
        select(
            User.id,
            User.full_name,
            Task.status,
            func.count(Task.id).label("count")
        )
        .join(TaskAssignee, User.id == TaskAssignee.user_id)
        .join(Task, TaskAssignee.task_id == Task.id)
        .group_by(User.id, Task.status)
    )).all()

    user_status_map = {}
    for user_id, full_name, status, count in status_data:
        if user_id not in user_status_map:
            user_status_map[user_id] = {
                "user_id": user_id,
                "user_name": full_name,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
            }
        user_status_map[user_id][status.value] = count

    overdue_result = (await session.execute(
        select(
            User.id,
            User.full_name,
            func.count(Task.id).label("overdue_tasks")
        )
        .join(TaskAssignee, User.id == TaskAssignee.user_id)
        .join(Task, TaskAssignee.task_id == Task.id)
        .where(Task.due_date < now.date(), Task.status != TaskStatus.completed)
        .group_by(User.id)
    )).all()
    overdue_data = {uid: count for uid, _, count in overdue_result}

    analytics = []
    for user_id, data in user_status_map.items():
        analytics.append({
            **data,
            "overdue": overdue_data.get(user_id, 0),
            "total_tasks": (
                data["pending"] + data["in_progress"] + data["completed"]
            )
        })
    unassigned_tasks = (await session.execute(
        select(Task.id, Task.title, Task.status, Task.due_date)
        .outerjoin(TaskAssignee, Task.id == TaskAssignee.task_id)
        .where(TaskAssignee.task_id.is_(None))
    )).all()
    unassigned_tasks = [
        {
            "id": tid,
            "title": title,
            "status": status.value if status else None,
            "due_date": due_date.isoformat() if due_date else None
        }
        for tid, title, status, due_date in unassigned_tasks
    ]

    return {
        "generated_at": now.isoformat(),
        "task_distribution": task_distribution,
        "analytics_per_user": analytics,
        "unassigned_tasks": {
            "count": len(unassigned_tasks),
            "tasks": unassigned_tasks,
        },
    }