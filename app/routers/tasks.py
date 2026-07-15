from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
)

from app.crud.task import (
    create_task,
    get_project_tasks,
    get_task_by_id,
    update_task,
    update_task_status,
    delete_task,

)
from app.crud.project import (
    get_project_by_id,
    get_project_membership,
)

router = APIRouter(
    tags=["Tasks"],
)


@router.post(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if project exists and current user is a member
    project, error = get_project_by_id(
        db,
        project_id,
        current_user.id,
    )

    if error == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if error == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    # Validate assigned user
    if task.assigned_to is not None:
        membership = get_project_membership(
            db,
            project_id,
            task.assigned_to,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user is not a project member",
            )

    # Prepare task data
    task_data = task.model_dump()

    task_data["project_id"] = project_id
    task_data["created_by"] = current_user.id

    # Create task
    new_task = create_task(
        db,
        task_data,
    )

    return new_task

@router.get("/projects/{project_id}/tasks")
def get_tasks(
    project_id: int,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check project exists and user is a member
    project, error = get_project_by_id(
        db,
        project_id,
        current_user.id,
    )

    if error == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if error == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    tasks = get_project_tasks(
        db=db,
        project_id=project_id,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    return tasks

@router.put("/tasks/{task_id}")
def update_project_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(
        db,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project, error = get_project_by_id(
        db,
        task.project_id,
        current_user.id,
    )

    if error == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if error == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    # Validate new assignee
    if task_update.assigned_to is not None:
        membership = get_project_membership(
            db,
            task.project_id,
            task_update.assigned_to,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user is not a project member",
            )

    updated_task = update_task(
        db,
        task,
        task_update,
    )

    return updated_task

@router.patch("/tasks/{task_id}/status")
def change_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(
        db,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project, error = get_project_by_id(
        db,
        task.project_id,
        current_user.id,
    )

    if error == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if error == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    updated_task = update_task_status(
        db,
        task,
        status_update.status,
    )

    return updated_task

@router.delete("/tasks/{task_id}")
def delete_project_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(
        db,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    membership = get_project_membership(
        db,
        task.project_id,
        current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    # Only project admin or task creator can delete
    if (
        membership.role != "admin"
        and task.created_by != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project admin or task creator can delete this task",
        )

    delete_task(
        db,
        task,
    )

    return {
        "message": "Task deleted successfully"
    }