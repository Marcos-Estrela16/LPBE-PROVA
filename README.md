# E-Commerce Catalog API — FastAPI & PostgreSQL

Esta é uma API REST desenvolvida em Python com o framework FastAPI e persistência relacional utilizando PostgreSQL. A aplicação e o banco de dados foram estruturados utilizando containers Docker para simplificar a execução e garantir um ambiente de desenvolvimento limpo.

---

## 🛠️ Tecnologias Utilizadas

- **FastAPI** — Criação das rotas REST e controle de injeção de dependências
- **SQLAlchemy 2.0** — Mapeamento objeto-relacional (ORM) e consultas
- **Pydantic V2** — Schemas para validação de payload e serialização das respostas
- **Pytest** — Suíte de testes automatizados de integração
- **Docker & Docker Compose** — Gerenciamento e orquestração do banco PostgreSQL

---

## 📂 Arquitetura do Projeto

A entrega contém os seguintes arquivos na estrutura raiz:

```text
prova_1_parceiro/
├── main.py              # Definição dos modelos ORM, schemas Pydantic e rotas
├── conftest.py          # Configurações de fixtures e overrides do banco de teste
├── requirements.txt     # Pacotes Python requeridos
├── docker-compose.yml   # Provisionamento dos containers de desenvolvimento e teste
├── Dockerfile           # Instruções de build do container do app
├── pytest.ini           # Definição do comportamento do Pytest
├── README.md            # Documentação e logs do sistema
└── tests/
    ├── __init__.py
    └── test_produtos.py # Suíte de testes (16 casos de teste atualizados)
```

---

## 🚀 Como Executar

### 1. Inicializar o Banco de Dados com Docker
Para iniciar o banco de dados de desenvolvimento local:
```bash
docker compose up -d postgres_db_dev
```

### 2. Rodar a API Localmente
Crie um ambiente virtual, instale as dependências e inicie a API com Uvicorn:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
A API estará acessível em: `http://localhost:8000`. O Swagger poderá ser visualizado em: `http://localhost:8000/docs`.

---

## 🧪 Executando a Suíte de Testes

A suíte de testes necessita do banco de testes real rodando em container separado (porta `5433`).

### 1. Iniciar o Banco de Teste
```bash
docker compose up -d postgres_db_test
```

### 2. Rodar o pytest
Execute o comando a seguir na pasta raiz do projeto:
```bash
pytest -v
```

---

## 🛡️ Isolamento entre os Testes

O isolamento é mantido usando fixtures do Pytest no arquivo `conftest.py`.
A fixture `client` intercepta cada execução de teste executando as seguintes etapas consecutivas:
1. **Setup**: Invoca `Base.metadata.create_all(bind=test_engine)` para criar um esquema de tabelas limpo no banco PostgreSQL de teste.
2. **Override**: Sobrescreve a dependência `get_database` do FastAPI para forçar o uso da `TestingSessionLocal`.
3. **Execution**: Cede a instância do `TestClient` para o teste rodar.
4. **Teardown**: Executa `Base.metadata.drop_all(bind=test_engine)` limpando completamente o banco antes do próximo teste.

Desta forma, garantimos isolamento de dados real, onde os testes podem rodar em qualquer ordem ou de forma assíncrona sem conflito de banco de dados.

---

## 📊 Saída Esperada do Pytest

```text
============================= test session starts ==============================
platform linux -- Python 3.14.5, pytest-9.1.0, pluggy-1.6.0 -- /home/eduardo/Temp/prova_1_parceiro/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/eduardo/Temp/prova_1_parceiro
configfile: pytest.ini
plugins: anyio-4.14.0, cov-7.1.0
collecting ... collected 16 items                                                             

tests/test_produtos.py::test_listagem_inicial_deve_retornar_vazio PASSED   [  6%]
tests/test_produtos.py::test_adicionar_produto_valido_sucesso PASSED       [ 12%]
tests/test_produtos.py::test_adicionar_produto_verifica_na_lista PASSED   [ 18%]
tests/test_produtos.py::test_buscar_detalhe_produto_por_id PASSED         [ 25%]
tests/test_produtos.py::test_buscar_produto_invalido_deve_retornar_404 PASSED [ 31%]
tests/test_produtos.py::test_excluir_produto_sucesso PASSED               [ 37%]
tests/test_produtos.py::test_excluir_produto_e_confirmar_inexistente PASSED [ 43%]
tests/test_produtos.py::test_excluir_produto_inexistente_retorna_404 PASSED [ 50%]
tests/test_produtos.py::test_criar_produto_com_dados_invalidos[dados_invalidos0] PASSED [ 56%]
tests/test_produtos.py::test_criar_produto_com_dados_invalidos[dados_invalidos1] PASSED [ 62%]
tests/test_produtos.py::test_criar_produto_com_dados_invalidos[dados_invalidos2] PASSED [ 68%]
tests/test_produtos.py::test_criar_produto_com_dados_invalidos[dados_invalidos3] PASSED [ 75%]
tests/test_produtos.py::test_criar_produto_com_dados_invalidos[dados_invalidos4] PASSED [ 81%]
tests/test_produtos.py::test_criar_produto_com_dados_invalidos[dados_invalidos5] PASSED [ 87%]
tests/test_produtos.py::test_persistencia_temporaria_isolamento_1 PASSED   [ 93%]
tests/test_produtos.py::test_persistencia_temporaria_isolamento_2 PASSED   [100%]

======================== 16 passed, 1 warning in 1.42s =========================
```
