import pytest, sys, os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.main import app


# Crie um banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependência para usar o banco de dados de teste
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_add_to_favorite(setup_database):
    response = client.post("/api/favorite/", json={"user_id": "user123", "video_id": "video123"})
    assert response.status_code == 200
    assert response.json()["user_id"] == "user123"
    assert response.json()["video_id"] == "video123"
    assert response.json()["statusfavorite"] is True
    
def test_check_favorite(setup_database):
    response = client.get("/api/favorite/status/video123?user_id=user123")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["statusfavorite"] is True

def test_remove_from_favorites(setup_database):
    response = client.delete("/api/favorite/video123?user_id=user123")
    print("Response from DELETE:", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Removed from favorites"
    

   # Check status again to ensure it's removed
    response = client.get("/api/favorite/status/video123?user_id=user123")
    print("Response from GET status:", response.json())
    assert response.status_code == 200
    assert response.json()["statusfavorite"] is False


def test_get_favorite_videos():
    user_id = str(uuid.uuid4())

    # Add multiple videos to the favorite list
    video_ids = [str(uuid.uuid4()) for _ in range(3)]
    for video_id in video_ids:
        client.post("/api/favorite/", json={"user_id": user_id, "video_id": video_id})

    # Retrieve the favorite list
    response = client.get(f"/api/favorite/?user_id={user_id}")
    assert response.status_code == 200
    assert "videoList" in response.json()
    video_list = response.json()["videoList"]

    # Check if the specific video is in the favorite list
    retrieved_video_ids = [item["video_id"] for item in video_list]
    for video_id in video_ids:
        assert video_id in retrieved_video_ids


