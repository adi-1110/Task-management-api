from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.schemas.project import ProjectCreate , ProjectUpdate
from app.models.user import User

def create_project(
    db: Session,
    project: ProjectCreate,
    owner_id: int,
):
    # Create the project
    db_project = Project(
        name=project.name,
        description=project.description,
        owner_id=owner_id,
    )

    db.add(db_project)

    # Flush so project.id is generated
    db.flush()

    # Add the creator as an admin member
    project_member = ProjectMember(
        project_id=db_project.id,
        user_id=owner_id,
        role="admin",
    )

    db.add(project_member)

    # Commit both inserts together
    db.commit()

    # Refresh project object
    db.refresh(db_project)

    return db_project

def get_user_projects(
    db: Session,
    user_id: int,
):
    return (
        db.query(Project)
        .join(
            ProjectMember,
            Project.id == ProjectMember.project_id,
        )
        .filter(ProjectMember.user_id == user_id)
        .all()
    )

def get_project_by_id(
    db: Session,
    project_id: int,
    user_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        return None, "not_found"

    membership = get_project_membership(
        db,
        project_id,
        user_id,
    )

    if membership is None:
        return None, "forbidden"

    return project, None

def update_project(
    db: Session,
    project_id: int,
    project_update: ProjectUpdate,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        return None

    update_data = project_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project

def delete_project(
    db: Session,
    project_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        return False

    db.delete(project)
    db.commit()

    return True

def add_project_member(
    db: Session,
    project_id: int,
    email: str,
    role: str,
):
    # Find the user
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        return None, "user_not_found"

    # Check if already a member
    existing = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        .first()
    )

    if existing:
        return None, "already_member"

    member = ProjectMember(
        project_id=project_id,
        user_id=user.id,
        role=role,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member, None

def get_project_membership(
    db: Session,
    project_id: int,
    user_id: int,
):
    return (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )

def is_project_member(
    db: Session,
    project_id: int,
    user_id: int,
):
    return (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
        is not None
    )
