import pytest
from fastapi.testclient import TestClient

from app.main import app


from app.core.database import Base, get_db

# Import all models so SQLAlchemy registers them
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task

from tests.database import engine, TestingSessionLocal
app.state.limiter.enabled = False

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client