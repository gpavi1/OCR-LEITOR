-- OCR-S1 - Base MySQL para OCR-LEITOR
-- Executar com usuário administrador do MySQL antes de usar o pipeline.

CREATE DATABASE IF NOT EXISTS ocr_leitor
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ocr_leitor;

CREATE TABLE IF NOT EXISTS clientes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    documento VARCHAR(32) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ativo',
    plano VARCHAR(50) NOT NULL DEFAULT 'starter',
    mensalidade_ativa BOOLEAN NOT NULL DEFAULT TRUE,
    vencimento_mensalidade DATE NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_clientes_status (status),
    INDEX idx_clientes_plano (plano)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS documentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    arquivo_nome VARCHAR(255) NOT NULL,
    arquivo_origem TEXT NULL,
    arquivo_destino TEXT NULL,
    arquivo_hash VARCHAR(128) NULL,
    tipo_documento VARCHAR(80) NULL,
    empresa VARCHAR(255) NULL,
    numero_nf VARCHAR(80) NULL,
    chave_acesso VARCHAR(80) NULL,
    vencimento DATE NULL,
    valor_total DECIMAL(12,2) NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'recebido',

    revisado BOOLEAN NOT NULL DEFAULT FALSE,
    revisado_por VARCHAR(120) NULL,
    revisado_em DATETIME NULL,
    observacao_revisao TEXT NULL,
    json_path TEXT NULL,
    ultimo_erro TEXT NULL,
    tentativas INT NOT NULL DEFAULT 0,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_documentos_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id),
    INDEX idx_documentos_cliente_status (cliente_id, status),
    INDEX idx_documentos_chave (chave_acesso),
    INDEX idx_documentos_hash (arquivo_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS integracoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    config_json JSON NULL,
    credencial_criptografada TEXT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_integracoes_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id),
    INDEX idx_integracoes_cliente_tipo (cliente_id, tipo),
    INDEX idx_integracoes_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS integracao_tentativas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    documento_id BIGINT NOT NULL,
    integracao_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL,
    destino_externo_id VARCHAR(255) NULL,
    erro TEXT NULL,
    resposta_resumida TEXT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tentativas_documento
        FOREIGN KEY (documento_id)
        REFERENCES documentos(id),
    CONSTRAINT fk_tentativas_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES integracoes(id),
    INDEX idx_tentativas_documento (documento_id),
    INDEX idx_tentativas_integracao_status (integracao_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cliente inicial para testes locais. Ajuste o nome depois.
INSERT INTO clientes (nome, plano)
SELECT 'Cliente Teste OCR', 'starter'
WHERE NOT EXISTS (SELECT 1 FROM clientes WHERE nome = 'Cliente Teste OCR');
