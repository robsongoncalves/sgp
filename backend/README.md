# Backend

API Flask para o Sistema de Gestao.

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Healthcheck: `GET http://localhost:5000/api/health`.

## Banco de dados

O backend ja esta preparado para PostgreSQL com SQLAlchemy e Flask-Migrate.

Configure a conexao pelo ambiente:

```bash
export DATABASE_URL=postgresql+psycopg://sgp:sgp@localhost:5432/sgp
```

Para subir um PostgreSQL local:

```bash
docker compose up -d postgres
```

Com o PostgreSQL rodando, os comandos de migracao ficam disponiveis pelo Flask:

```bash
export FLASK_APP=run.py
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

Para importar os dados atuais dos arquivos JSON para o PostgreSQL:

```bash
flask seed-json
```

Em um banco descartavel de desenvolvimento, tambem e possivel limpar e reimportar:

```bash
flask seed-json --reset
```

## Documentacao da API

Swagger UI: `GET http://localhost:5000/api/docs`

OpenAPI JSON: `GET http://localhost:5000/api/openapi.json`
