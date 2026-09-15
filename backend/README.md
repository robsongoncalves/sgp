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

## Armazenamento de anexos

Nesta primeira versao, os anexos serao salvos em repositorio local. A escolha do
driver fica preparada por variavel de ambiente para permitir evolucao futura para
MinIO.

```bash
export ATTACHMENT_STORAGE_DRIVER=local
export ATTACHMENT_LOCAL_PATH=storage/uploads
```

Drivers previstos:

- `local`: salva arquivos no caminho configurado em `ATTACHMENT_LOCAL_PATH`.
- `minio`: reservado para integracao futura com storage S3 compativel.

## Documentacoes

O cadastro fica em `/admin/documentacoes`, na area restrita. Permite listar,
pesquisar, criar, editar e excluir documentacoes com URL, descricao e topicos
para importacao. A importacao preenche a descricao para revisao; clique em Salvar
para persistir. O cadastro de servicos seleciona uma documentacao existente.
Atualizar uma documentacao atualiza o conteudo exibido pelos servicos vinculados.
Documentacoes em uso nao podem ser excluidas.

Execute `python -m flask --app run.py db upgrade` para criar o catalogo e migrar
os conteudos existentes, preservando descricoes distintas para a mesma URL.
API: `/api/documentations`, `/api/documentations/<id>` e
`POST /api/documentations/import`. Servicos recebem `documentation_id` (ou null
para remover o vinculo); as respostas continuam incluindo descricao e URL.

Verificacao: `python -m unittest discover -s tests`. Os testes de integracao
usam o banco configurado e desfazem as alteracoes ao finalizar.

A flag `sync_enabled` (desativada por padrao) inclui a documentacao na rotina
`POST /api/documentations/sync`, acionada por **Sincronizar tudo** na listagem.
A rotina salva as descricoes importadas e retorna `total`, `updated`, `failed`
e `errors`. Uma falha ou conteudo vazio preserva a descricao anterior e nao
interrompe as demais importacoes. Uma lista de topicos vazia importa todo o
conteudo de `entry-content`, ou do conteudo principal da pagina quando ausente.
Essa regra tambem vale para a importacao individual, que continua exigindo Salvar.

## Cancelamento de solicitacoes

`POST /api/service-requests/<id>/cancel` recebe `user_id`, seguindo o padrao de
identificacao de usuario das demais acoes da API. Somente o solicitante pode
cancelar uma solicitacao ainda nao concluida. A operacao registra data, usuario
e movimentacao, preserva situacao anterior, formulario, documentos e anexos.
Chamadas repetidas nao duplicam o registro. Solicitacoes canceladas permanecem
consultaveis, bloqueiam alteracoes e deixam de ser reutilizadas ao iniciar o
servico; seus documentos tambem deixam a fila de pendencias.
