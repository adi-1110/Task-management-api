from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')",
            name="check_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="check_priority",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(String)

    status = Column(
        String,
        nullable=False,
        default="todo",
    )

    priority = Column(
        String,
        nullable=False,
        default="medium",
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    due_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships

    project = relationship(
        "Project",
        back_populates="tasks",
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_tasks",
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_tasks",
    )