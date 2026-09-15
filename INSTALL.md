# Instalacao

Guia rapido para instalar e executar o frontend Angular e o backend Flask.

## Windows (PowerShell)

Use Node.js 20.19.x, Python 3.11 e Docker Desktop com containers Linux.
O `psycopg-binary==3.2.1` fixado no projeto nao possui pacote para Python 3.13
no Windows. Crie o ambiente virtual com Python 3.11.

Na raiz do repositorio:

```powershell
docker compose -f backend/compose.yaml up -d postgres
docker compose -f backend/compose.yaml ps
```

Prepare o backend (substitua `py -3.11` pelo caminho do Python 3.11 se nao
utilizar o Python Launcher):

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m flask --app run.py db upgrade
.\.venv\Scripts\python.exe -m flask --app run.py run --no-reload --port 5000
```

O comando Flask carrega o `.env`. Em um banco novo e vazio, execute
`.\.venv\Scripts\python.exe -m flask --app run.py seed-json` antes de iniciar
a API. Nao execute o seed em banco existente sem revisar os dados: ele atualiza
registros pelos IDs dos arquivos JSON.

Em outro terminal, a partir da raiz, inicie o Angular:

```powershell
cd frontend
npm.cmd ci
npm.cmd start -- --host 127.0.0.1
```

Em um terceiro terminal, a partir da raiz, inicie o portal publico Astro:

```powershell
cd frontend_public
if (!(Test-Path .env)) { Copy-Item .env.example .env }
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1
```

- API: http://localhost:5000/api/health
- Angular: http://localhost:4200
- Portal publico: http://localhost:4321
- Cadastro de Servicos: http://localhost:4200/admin/servicos (login administrador)

### Testar a importacao WordPress

Abra um servico no cadastro e informe a URL
`https://sites.unipampa.edu.br/dap/abono-de-permanencia/`. Mantenha os topicos
`DEFINICAO, QUEM FAZ?` e clique em **Importar**. A descricao deve receber as
duas secoes; revise antes de salvar.

O cadastro importa HTML e aceita tanto HTML quanto texto simples na descricao,
com reconhecimento automatico. Links, listas, tabelas e imagens dos topicos sao
preservados; scripts, estilos e atributos executaveis sao removidos. URLs relativas
de links e imagens sao resolvidas em relacao a pagina de origem. O HTML e gravado
ao clicar em **Salvar**. Descricoes antigas continuam compativeis.

Na API, envie `output_format: "html"` para importar HTML. O padrao `text` mantem
compatibilidade com integracoes anteriores. As respostas de servicos incluem
`description_html` (sanitizado para renderizacao) e `description_text` (resumos),
alem de `description` (conteudo editavel).

Para verificar a API diretamente:

```powershell
$payload = @{ url = 'https://sites.unipampa.edu.br/dap/abono-de-permanencia/' } | ConvertTo-Json
Invoke-RestMethod http://localhost:5000/api/services/documentation/extract `
  -Method Post -ContentType 'application/json' -Body $payload
```

O campo `fetch_method` indica `http` ou `playwright`. O fallback so e acionado
quando a tentativa HTTP falha; uma resposta sem as secoes esperadas nao aciona
o navegador automaticamente.

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
