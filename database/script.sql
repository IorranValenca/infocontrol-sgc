-- Script de criação do banco de dados InfoControl
-- Sistema de Gestão Comercial para Loja de Informática

CREATE TABLE usuarios (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(20) NOT NULL,
    CONSTRAINT chk_usuario_perfil
        CHECK (perfil IN ('ADMIN', 'FUNCIONARIO'))
);

CREATE TABLE clientes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    endereco VARCHAR(150),
    CONSTRAINT chk_cliente_email
        CHECK (POSITION('@' IN email) > 1)
);

CREATE TABLE produtos (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    preco NUMERIC(10,2) NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_produto_preco
        CHECK (preco >= 0),
    CONSTRAINT chk_produto_quantidade
        CHECK (quantidade_estoque >= 0),
    CONSTRAINT chk_produto_estoque_minimo
        CHECK (estoque_minimo >= 0)
);

CREATE TABLE vendas (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    data_venda TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cliente_id BIGINT NOT NULL,
    usuario_id BIGINT NOT NULL,
    valor_total NUMERIC(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_vendas_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_vendas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    CONSTRAINT chk_venda_valor_total
        CHECK (valor_total >= 0)
);

CREATE TABLE itens_venda (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    venda_id BIGINT NOT NULL,
    produto_id BIGINT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    CONSTRAINT fk_itens_venda_venda
        FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    CONSTRAINT fk_itens_venda_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
    CONSTRAINT chk_item_quantidade
        CHECK (quantidade > 0),
    CONSTRAINT chk_item_preco_unitario
        CHECK (preco_unitario >= 0),
    CONSTRAINT chk_item_subtotal
        CHECK (subtotal >= 0)
);
