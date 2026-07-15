from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'member', 'viewer')",
            name="check_role",
        ),
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role = Column(
        String,
        nullable=False,
        default="member",
    )

    # Relationships

    project = relationship(
        "Project",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="project_memberships",
    )