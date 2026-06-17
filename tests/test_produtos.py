import pytest

# Testes automatizados para validação do estoque com nomes e payloads diferenciados

# 1. Listar produtos quando o banco está vazio
def test_listagem_inicial_deve_retornar_vazio(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

# 2. Criar produto e verificar persistência no banco
def test_adicionar_produto_valido_sucesso(client):
    payload = {
        "nome": "Carregador Portatil USB-C",
        "preco": 149.99,
        "estoque": 40,
        "ativo": True
    }
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["nome"] == payload["nome"]
    assert data["preco"] == payload["preco"]
    assert data["estoque"] == payload["estoque"]
    assert data["ativo"] == payload["ativo"]

# 3. Criar produto e verificar que aparece na listagem
def test_adicionar_produto_verifica_na_lista(client):
    payload = {
        "nome": "Cabo HDMI 2.1 2m",
        "preco": 65.50,
        "estoque": 100,
        "ativo": True
    }
    # Cria
    post_res = client.post("/produtos", json=payload)
    assert post_res.status_code == 201
    
    # Lista
    get_res = client.get("/produtos")
    assert get_res.status_code == 200
    
    produtos = get_res.json()
    assert len(produtos) == 1
    assert produtos[0]["nome"] == payload["nome"]

# 4. Buscar produto por id — caso de sucesso
def test_buscar_detalhe_produto_por_id(client, produto_existente):
    response = client.get(f"/produtos/{produto_existente.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == produto_existente.id
    assert data["nome"] == produto_existente.nome
    assert data["preco"] == produto_existente.preco

# 5. Buscar produto com id inexistente — deve retornar 404
def test_buscar_produto_invalido_deve_retornar_404(client):
    response = client.get("/produtos/101010")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não localizado no banco"

# 6. Deletar produto — deve retornar 204
def test_excluir_produto_sucesso(client, produto_existente):
    response = client.delete(f"/produtos/{produto_existente.id}")
    assert response.status_code == 204
    assert response.text == ""

# 7. Deletar produto e confirmar remoção com GET subsequente
def test_excluir_produto_e_confirmar_inexistente(client, produto_existente):
    # Deleta
    del_res = client.delete(f"/produtos/{produto_existente.id}")
    assert del_res.status_code == 204
    
    # Tenta buscar
    get_res = client.get(f"/produtos/{produto_existente.id}")
    assert get_res.status_code == 404

# 8. Deletar produto inexistente — deve retornar 404
def test_excluir_produto_inexistente_retorna_404(client):
    response = client.delete("/produtos/202020")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não localizado no banco"

# 9. Pelo menos 1 teste parametrizado com @pytest.mark.parametrize cobrindo payloads inválidos (status 422)
@pytest.mark.parametrize(
    "dados_invalidos",
    [
        {"nome": "", "preco": 80.0, "estoque": 10, "ativo": True},       # Nome vazio
        {"nome": "   ", "preco": 20.0, "estoque": 5, "ativo": True},     # Nome apenas com espaços
        {"nome": "Teclado X", "preco": 0.0, "estoque": 1, "ativo": True},  # Preço zero
        {"nome": "Teclado Y", "preco": -5.99, "estoque": 2, "ativo": True}, # Preço negativo
        {"preco": 49.90, "estoque": 12},                                   # Ausência de nome
        {"nome": "Teclado Z", "estoque": 8},                                # Ausência de preço
    ]
)
def test_criar_produto_com_dados_invalidos(client, dados_invalidos):
    response = client.post("/produtos", json=dados_invalidos)
    assert response.status_code == 422

# 10. Pelo menos 1 teste que valide que o banco está isolado entre execuções
def test_persistencia_temporaria_isolamento_1(client):
    payload = {
        "nome": "Hub USB-C 7 em 1",
        "preco": 259.00,
        "estoque": 15,
        "ativo": True
    }
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    
    get_res = client.get("/produtos")
    assert len(get_res.json()) == 1

def test_persistencia_temporaria_isolamento_2(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []
