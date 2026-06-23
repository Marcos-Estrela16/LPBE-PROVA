import pytest

# Testes automatizados para validação do estoque com nomes e payloads diferenciados

# 1. Listar produtos quando o banco está vazio
def test_deve_retornar_lista_vazia_quando_nenhum_produto_cadastrado(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

# 2. Criar produto e verificar persistência no banco
def test_deve_salvar_novo_produto_com_sucesso(client):
    payload = {
        "nome": "Moedor de Café Manual em Inox",
        "preco": 129.90,
        "estoque": 20,
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
def test_produto_recem_criado_deve_aparecer_no_catalogo(client):
    payload = {
        "nome": "Filtro de Papel Hario V60",
        "preco": 35.00,
        "estoque": 50,
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
def test_deve_retornar_detalhes_corretos_ao_buscar_por_id(client, produto_existente):
    response = client.get(f"/produtos/{produto_existente.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == produto_existente.id
    assert data["nome"] == produto_existente.nome
    assert data["preco"] == produto_existente.preco

# 5. Buscar produto com id inexistente — deve retornar 404
def test_deve_retornar_404_para_produto_fora_do_catalogo(client):
    response = client.get("/produtos/101010")
    assert response.status_code == 404
    assert response.json()["detail"] == "Vish, não encontramos nenhum produto com esse ID no catálogo."

# 6. Deletar produto — deve retornar 204
def test_deve_remover_produto_do_catalogo_com_sucesso(client, produto_existente):
    response = client.delete(f"/produtos/{produto_existente.id}")
    assert response.status_code == 204
    assert response.text == ""

# 7. Deletar produto e confirmar remoção com GET subsequente
def test_apos_remover_produto_nao_deve_mais_ser_encontrado(client, produto_existente):
    # Deleta
    del_res = client.delete(f"/produtos/{produto_existente.id}")
    assert del_res.status_code == 204
    
    # Tenta buscar
    get_res = client.get(f"/produtos/{produto_existente.id}")
    assert get_res.status_code == 404

# 8. Deletar produto inexistente — deve retornar 404
def test_deve_retornar_404_ao_tentar_excluir_produto_fantasma(client):
    response = client.delete("/produtos/202020")
    assert response.status_code == 404
    assert response.json()["detail"] == "Vish, não encontramos nenhum produto com esse ID no catálogo."

# 9. Pelo menos 1 teste parametrizado com @pytest.mark.parametrize cobrindo payloads inválidos (status 422)
@pytest.mark.parametrize(
    "dados_invalidos",
    [
        {"nome": "", "preco": 80.0, "estoque": 10, "ativo": True},       # Nome vazio
        {"nome": "   ", "preco": 20.0, "estoque": 5, "ativo": True},     # Nome apenas com espaços
        {"nome": "Prensa Francesa", "preco": 0.0, "estoque": 1, "ativo": True},  # Preço zero
        {"nome": "Caneca Térmica", "preco": -5.99, "estoque": 2, "ativo": True}, # Preço negativo
        {"preco": 49.90, "estoque": 12},                                   # Ausência de nome
        {"nome": "Balança de Precisão", "estoque": 8},                                # Ausência de preço
    ]
)
def test_nao_deve_permitir_cadastro_com_dados_mal_formatados(client, dados_invalidos):
    response = client.post("/produtos", json=dados_invalidos)
    assert response.status_code == 422

# 10. Pelo menos 1 teste que valide que o banco está isolado entre execuções
def test_valida_isolamento_de_estado_no_banco_parte_1(client):
    payload = {
        "nome": "Cafeteira Italiana Moka",
        "preco": 189.90,
        "estoque": 20,
        "ativo": True
    }
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    
    get_res = client.get("/produtos")
    assert len(get_res.json()) == 1

def test_valida_isolamento_de_estado_no_banco_parte_2(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []
