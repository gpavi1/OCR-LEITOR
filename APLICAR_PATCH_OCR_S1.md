# OCR-S1 — JSON padrão + MySQL de controle

Este patch adiciona uma camada nova sem apagar o OCR atual.

## 1. Copiar arquivos

Copie estas pastas/arquivos para dentro de `OCR-LEITOR`:

```text
database/
models/
exporters/
utils/
ocr_pipeline_s1.py
.env.example.mysql
requirements.add.txt
```

## 2. Instalar dependência MySQL

```powershell
pip install mysql-connector-python
```

## 3. Criar `.env`

Copie `.env.example.mysql` para `.env` e preencha `DB_PASSWORD`.

## 4. Criar banco e tabelas

Abra o MySQL como administrador e execute:

```sql
SOURCE caminho/para/OCR-LEITOR/database/schema.sql;
```

Ou cole o conteúdo de `database/schema.sql` no cliente MySQL.

## 5. Criar usuário do app no MySQL

Use uma senha forte diferente da senha do root:

```sql
CREATE USER IF NOT EXISTS 'ocr_app'@'localhost' IDENTIFIED BY 'trocar_por_senha_forte';
GRANT SELECT, INSERT, UPDATE, DELETE ON ocr_leitor.* TO 'ocr_app'@'localhost';
FLUSH PRIVILEGES;
```

## 6. Testar sem mover arquivos

```powershell
python ocr_pipeline_s1.py --cliente-id 1 --no-move
```

Resultado esperado:

```text
output/json/<arquivo>.json
registro no MySQL, se o banco estiver configurado
```

## 7. Depois testar com movimentação

```powershell
python ocr_pipeline_s1.py --cliente-id 1
```

Arquivos com extração completa vão para `processed/`. Arquivos parciais vão para `erro/` para revisão.

## Observações de segurança

- Não suba `config/settings.json` no GitHub.
- Não suba `.env` no GitHub.
- Tokens do Monday devem ficar fora do código.
- O token presente no ZIP enviado deve ser considerado exposto e substituído/rotacionado no Monday.
