# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.main import app
# from app.models.database import Base
# from app.dependencies import get_db
# import uuid


# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(bind=engine)


# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)


# @pytest.fixture
# def unique_username():
#     return f"testuser_{uuid.uuid4()}"


# @pytest.fixture
# def get_token(unique_username):
#     client.post(
#         "/v1/register", json={"username": unique_username, "password": "testpassword"}
#     )
#     response = client.post(
#         "/v1/login", data={"username": unique_username, "password": "testpassword"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     return data["data"]["access_token"]


# def test_register(unique_username):
#     response = client.post(
#         "/v1/register", json={"username": unique_username, "password": "newpassword"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["data"]["username"] == unique_username


# def test_login(unique_username):
#     client.post(
#         "/v1/register", json={"username": unique_username, "password": "newpassword"}
#     )
#     response = client.post(
#         "/v1/login", data={"username": unique_username, "password": "newpassword"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert "access_token" in data["data"]


# def test_profile(get_token):
#     token = get_token
#     response = client.get("/v1/profile", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["data"]["username"]


# def test_protected_resource(get_token):
#     token = get_token
#     response = client.get(
#         "/v1/protected-resource", headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert data["data"]["message"] == "You have accessed a protected resource"


# def test_refresh_token(get_token):
#     token = get_token
#     response = client.post(
#         "/v1/refresh-token", headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert "access_token" in data["data"]
