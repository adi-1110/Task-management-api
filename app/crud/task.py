from sqlalchemy.orm import Session
from app.schemas.task import TaskUpdate
from app.models.task import Task


def create_task(db: Session, task_data: dict):
    task = Task(**task_data)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

def get_project_tasks(
    db: Session,
    project_id: int,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
):
    query = db.query(Task).filter(Task.project_id == project_id)

    # Filters
    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    # Sorting
    allowed_sort_fields = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "status": Task.status,
        "title": Task.title,
    }

    sort_column = allowed_sort_fields.get(sort_by, Task.created_at)

    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    offset = (page - 1) * page_size

    return (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

def get_task_by_id(
    db: Session,
    task_id: int,
):
    return (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

def update_task(
    db: Session,
    task: Task,
    task_update: TaskUpdate,
):
    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task

def update_task_status(
    db: Session,
    task: Task,
    status: str,
):
    task.status = status

    db.commit()
    db.refresh(task)

    return task

def delete_task(
    db: Session,
    task: Task,
):
    db.delete(task)
    db.commit()

    return True