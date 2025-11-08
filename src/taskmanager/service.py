from fastapi import HTTPException
from models.task import Task, TaskAssignee, TaskStatus, TaskDependency
from sqlmodel import select, delete

async def update_task_object(inc_task, user, session):
    task = await session.get(Task, inc_task.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.created_by != user.id:
        assigned = (await session.execute(
            select(TaskAssignee)
            .where(TaskAssignee.task_id == task.id, TaskAssignee.user_id == user.id)
        )).scalars().first()
        if not assigned:
            raise HTTPException(status_code=403, detail="Not authorized to modify this task")
    if task.status == TaskStatus.completed:
        raise HTTPException(status_code=400, detail="Cannot update a completed task")
    for field, value in inc_task.model_dump(exclude_unset=True).items():
        if hasattr(task, field) and field not in ("assignee_ids", "depends_on_ids", "blocked_by_ids", "id"):
            setattr(task, field, value)
    if inc_task.assignee_ids is not None:
        # Remove existing links
        await session.execute(delete(TaskAssignee).where(TaskAssignee.task_id == task.id))
        # Add new ones
        new_assignees = [TaskAssignee(task_id=task.id, user_id=uid) for uid in inc_task.assignee_ids]
        session.add_all(new_assignees)
    if inc_task.depends_on_ids is not None:
        await session.execute(delete(TaskDependency).where(TaskDependency.task_id == task.id))
        new_dependencies = [
            TaskDependency(task_id=task.id, depends_on_task_id=dep_id)
            for dep_id in inc_task.depends_on_ids
        ]
        session.add_all(new_dependencies)
    if inc_task.blocked_by_ids is not None:
        await session.execute(delete(TaskDependency).where(TaskDependency.depends_on_task_id == task.id))
        new_blocked = [
            TaskDependency(task_id=blk_id, depends_on_task_id=task.id)
            for blk_id in inc_task.blocked_by_ids
        ]
        session.add_all(new_blocked)
    if inc_task.status == TaskStatus.completed:
        subtasks = (await session.execute(select(Task).where(Task.parent_task_id == task.id))).scalars().all()
        incomplete_subs = [t for t in subtasks if t.status != TaskStatus.completed]

        blocking_tasks = (await session.execute(
            select(Task)
            .join(TaskDependency, Task.id == TaskDependency.task_id)
            .where(TaskDependency.depends_on_task_id == task.id)
        )).scalars().all()
        incomplete_blockers = [t for t in blocking_tasks if t.status != TaskStatus.completed]

        if incomplete_subs or incomplete_blockers:
            raise HTTPException(
                status_code=400,
                detail="Cannot mark this task as completed while subtasks or blocking tasks are incomplete."
            )
    return True