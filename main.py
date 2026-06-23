import os
import sys
from typing import List, Generator
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Configuração do Banco de Dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://db_admin:db_pass_2026@localhost:5432/store_development"
)

db_engine = create_engine(DATABASE_URL)
SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

# 2. Modelo ORM do SQLAlchemy
class ProductModel(Base):
    __tablename__ = "store_items"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)

# 3. Schemas de Validação do Pydantic
class ProductCreate(BaseModel):
    nome: str
    preco: float
    estoque: int = 0
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def checar_nome(cls, val: str) -> str:
        if not val or not val.strip():
            raise ValueError("Ops! Todo produto precisa de um nome válido.")
        return val.strip()

    @field_validator("preco")
    @classmethod
    def checar_preco(cls, val: float) -> float:
        if val <= 0:
            raise ValueError("O valor do produto não pode ser gratuito ou negativo.")
        return val

class ProductSchema(BaseModel):
    id: int
    nome: str
    preco: float
    estoque: int
    ativo: bool

    model_config = {
        "from_attributes": True
    }

# 4. Inicialização do App FastAPI
app = FastAPI(
    title="Boutique de Cafés Especiais - API",
    description="Gerenciamento de estoque para uma loja de cafés artesanais e acessórios.",
    version="1.0.0"
)

# 5. Dependency Injection para Sessão do Banco
def get_database() -> Generator[Session, None, None]:
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()

# 6. Endpoints Obrigatórios
@app.get("/produtos", response_model=List[ProductSchema], status_code=status.HTTP_200_OK)
def get_all_products(db: Session = Depends(get_database)):
    query = select(ProductModel)
    return db.execute(query).scalars().all()

@app.post("/produtos", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_database)):
    db_product = ProductModel(
        nome=product.nome,
        preco=product.preco,
        estoque=product.estoque,
        ativo=product.ativo
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/produtos/{id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
def get_product_by_id(id: int, db: Session = Depends(get_database)):
    item = db.get(ProductModel, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vish, não encontramos nenhum produto com esse ID no catálogo."
        )
    return item

@app.delete("/produtos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_by_id(id: int, db: Session = Depends(get_database)):
    item = db.get(ProductModel, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vish, não encontramos nenhum produto com esse ID no catálogo."
        )
    db.delete(item)
    db.commit()
    return None

# Criar tabelas se não estiver em ambiente de teste
if "pytest" not in sys.modules:
    Base.metadata.create_all(bind=db_engine)
