from pydantic import BaseModel
from typing import Optional ,Literal

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int

    model_config = {
        "from_attributes": True
    }

class ProjectMemberCreate(BaseModel):
    email: str
    role: Literal["admin", "member", "viewer"] = "member"