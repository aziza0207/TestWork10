import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from ..models import User
from ..database import Base
from ..main import app
from ..models.user import bcrypt_context
from ..dependencies import get_db_session
from ..models import Service
from ..utils.enums import ServiceStatus

SQLALCHEMY_DATABASE_URL = "postgresql://fastapi:fastapi@test-db/test"

engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture()
def client(db_session):
    return TestClient(app)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture()
def user(db_session):
    hashed_pw = bcrypt_context.hash("TestPassword")
    user = User(name="TestUser", email="azizamukashkyzy@gmail.com", password=hashed_pw)
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture()
def auth_header(client, user):
    response = client.post(
        "/auth/token/",
        data={"username": user.email, "password": "TestPassword"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def service(db_session, user):
    new_service = Service(
        title="Test Service",
        owner_id=user.id,
        user=user,
        status=ServiceStatus.PENDING,
        description="A test service.",
        priority=1,
    )

    db_session.add(new_service)
    db_session.commit()
    db_session.refresh(new_service)

    yield new_service

    db_session.delete(new_service)
    db_session.commit()
