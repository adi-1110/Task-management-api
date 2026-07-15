from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.project import create_project,add_project_member
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectMemberCreate
)
from typing import List
from app.crud.project import get_user_projects

from fastapi import HTTPException
from app.crud.project import get_project_by_id

from app.dependencies.auth import require_role
from app.crud.project import update_project
from app.crud.project import delete_project

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)
@router.post(
    "",
    response_model=ProjectResponse,
)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_project(
        db=db,
        project=project,
        owner_id=current_user.id,
    )


@router.get(
    "",
    response_model=List[ProjectResponse],
)
def list_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_user_projects(
        db=db,
        user_id=current_user.id,
    )

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project, error = get_project_by_id(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    if error == "not_found":
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if error == "forbidden":
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this project",
        )

    return project

@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_role("admin")),
):
    updated_project = update_project(
        db=db,
        project_id=project_id,
        project_update=project,
    )

    if updated_project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return updated_project

@router.delete(
    "/{project_id}",
    status_code=204,
)
def delete_existing_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_role("admin")),
):
    deleted = delete_project(
        db=db,
        project_id=project_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
    
@router.post("/{project_id}/members")
def add_member(
    project_id: int,
    member: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_role("admin")),
):
    result, error = add_project_member(
        db=db,
        project_id=project_id,
        email=member.email,
        role=member.role,
    )

    if error == "user_not_found":
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if error == "already_member":
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this project",
        )

    return {
        "message": "Member added successfully"
    }