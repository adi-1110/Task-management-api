from fastapi import FastAPI , HTTPException

from app.routers import auth

from fastapi import Depends
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.routers import projects , tasks

from fastapi.exceptions import RequestValidationError

from app.exceptions.handlers import (
    http_exception_handler,
    validation_exception_handler,
)

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.core.rate_limit import limiter

app = FastAPI()

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/projects")
def get_projects(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": f"Welcome {current_user.name}",
        "projects": []
    }

app.add_exception_handler(
    HTTPException,
    http_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

@app.get("/health")
def health():
    return {"status": "healthy"}