import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.routers.buscas import limiter

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture()
def client(monkeypatch):
    # Testes nunca devem chamar a API real, mesmo que .env tenha uma chave
    # configurada para uso manual/local — garante resultado determinístico.
    monkeypatch.setattr(settings, "google_places_api_key", None)

    # O limiter é um objeto global (module-level), então sem resetar aqui o
    # contador de "10/minute" acumula entre testes de arquivos diferentes e
    # os últimos da suíte tomam 429 sem relação nenhuma com o que testam.
    limiter.reset()

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
