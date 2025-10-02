# JarVault API

JarVault é uma API para armazenamento, listagem, download e exclusão de arquivos JAR, construída com FastAPI e SQLAlchemy.

## Funcionalidades
- Upload de arquivos JAR (individual ou em lote)
- Listagem de arquivos JAR
- Download de arquivos JAR
- Exclusão individual ou em lote de arquivos JAR (com senha)

## Requisitos
- Python 3.12+
- SQLite (default, pode ser adaptado)

## Instalação
```bash
# Clone o repositório
$ git clone https://github.com/Andre-PI/jarvault.git
$ cd jarvault

# Instale as dependências
$ pip install -r requirements.txt
```

## Configuração
Edite o arquivo `app/config.py` para definir o diretório de armazenamento e a senha de exclusão:
```python
# app/config.py
storage_dir = "./storage"
delete_password = "sua_senha"
```

## Executando o servidor
```bash
$ uvicorn main:app --reload
```
A API estará disponível em: [http://localhost:8000](http://localhost:8000)

## CORS
A API permite requisições do frontend rodando em `http://localhost:8080`.

## Endpoints principais
- `POST /api/jars` — Upload de um JAR
- `POST /api/jars/bulk` — Upload de múltiplos JARs
- `GET /api/jars` — Listar JARs
- `GET /api/jars/{jar_id}` — Detalhes de um JAR
- `GET /api/jars/{jar_id}/download` — Download de um JAR
- `DELETE /api/jars/{jar_id}` — Excluir JAR individual (requer senha)
- `DELETE /api/jars/bulk` — Excluir múltiplos JARs (requer senha)

## Exemplo de requisição para exclusão em lote
```json
{
  "jar_ids": [1, 2, 3],
  "password": "sua_senha"
}
```

## Licença
MIT
