import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importa o app, o Base, o modelo e a dependência get_database
from main import app, Base, get_database, ProductModel

# URL do banco de dados de teste (rodando no container postgres_db_test_container na porta 5433)
TEST_DATABASE_URL = "postgresql://db_admin:db_pass_2026@localhost:5433/store_testing"

# Cria a engine e a session factory para o banco de teste
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(name="client")
def client_fixture():
    # Cria todas as tabelas no banco de teste antes de rodar os testes
    Base.metadata.create_all(bind=test_engine)

    # Função local para substituir a dependência get_database
    def override_get_database():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Sobrescreve a dependência get_database no app FastAPI
    app.dependency_overrides[get_database] = override_get_database

    # Faz o yield do TestClient para os testes consumirem
    with TestClient(app) as client:
        yield client

    # Limpa as dependências sobrescritas
    app.dependency_overrides.clear()

    # Destrói todas as tabelas no banco de teste após a execução do teste
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(name="produto_existente")
def produto_existente_fixture(client):
    # Fixture auxiliar que depende de client e já cria um produto no banco
    db = TestingSessionLocal()
    try:
        sample = ProductModel(
            nome="Café Moído - Torra Média 250g",
            preco=45.50,
            estoque=100,
            ativo=True
        )
        db.add(sample)
        db.commit()
        db.refresh(sample)
        return sample
    finally:
        db.close()
