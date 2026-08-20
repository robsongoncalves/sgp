# Instalacao

Guia rapido para instalar e executar o frontend Angular e o backend Flask.

## Frontend

```bash
cd frontend
npm install
npm start
```

Por padrao, a aplicacao ficara disponivel em:

```text
http://localhost:4200
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Healthcheck:

```text
GET http://localhost:5000/api/health
```
