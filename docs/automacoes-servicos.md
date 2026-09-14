# Automacoes de Servicos

## Objetivo

Automacoes de servicos permitem executar functions Python em eventos do ciclo de vida de um servico. A opcao adotada no projeto segue a ideia do OpenWebUI: a function fica cadastrada no banco, pode ser ativada/inativada no CRUD e e associada ao servico no cadastro de Servicos.

Tambem continuamos suportando `handler_key` para handlers versionados dentro do codigo, mas o uso preferencial passa a ser a function cadastrada.

## Eventos iniciais

- `before_request_create`: executado quando o usuario inicia um servico, antes de criar ou retornar uma solicitacao inicial existente.
- `after_request_create`: executado apos criar uma nova solicitacao.

## Contexto recebido pelo handler

Todo handler recebe um dicionario `context`:

```python
{
    "event": "before_request_create",
    "service": {
        "id": 90,
        "name": "Calculadora de Pontuacao Progressao Docente",
        "slug": "calculadora-de-pontuacao-progressao-docente",
        "module_key": "calculadora-pontuacao-docente",
    },
    "user": {
        "id": 5,
        "name": "Charles Quevedo Carpes",
        "email": "charlescarpes@unipampa.edu.br",
        "siape": "1000005",
        "cargo": "Professor do Magisterio Superior",
        "classe_nivel": "Classe A - Adjunto A",
        "local_exercicio": "Campus Alegrete",
        "telefone": "",
    },
    "request": {
        "id": None,
        "number": None,
        "status": None,
        "form_data": {},
        "created_at": None,
        "updated_at": None,
    },
    "config": {
        "connection": "db2_guri",
        "periodo_meses": 24,
        "usar_cache": True,
    },
}
```

## Retorno esperado

O handler deve retornar um dicionario. O campo mais importante e `form_data_patch`, que e mesclado ao `form_data` da solicitacao.

```python
def handle(context):
    return {
        "form_data_patch": {
            "pontuacao": {
                "importados": {}
            }
        },
        "messages": ["Dados importados."],
        "warnings": []
    }
```

## Cadastro no banco

Tabela `automation_functions`:

- `name`
- `slug`
- `description`
- `language`
- `source_code`
- `timeout_seconds`
- `active`

Tabela `service_hooks`:

- `service_id`
- `function_id`
- `event_name`
- `handler_key`
- `config`
- `execution_order`
- `active`

Quando `function_id` estiver preenchido, o backend executa o codigo Python salvo em `automation_functions.source_code`. Quando `function_id` estiver vazio, o `handler_key` aponta para um modulo dentro de `backend/app/service_hooks/handlers`.

Exemplo:

```json
{
  "service_id": 90,
  "event_name": "before_request_create",
  "function_id": 1,
  "handler_key": "",
  "config": {
    "connection": "db2_guri",
    "periodo_meses": 24
  }
}
```

## CRUD

No frontend administrativo existe a rota `/admin/functions` para cadastrar functions. No cadastro de Servicos, a secao `Automações do serviço` permite selecionar o evento, a function, a ordem de execucao e a configuracao JSON.

Toda function Python deve expor uma funcao:

```python
def handle(context):
    return {
        "form_data_patch": {},
        "messages": [],
        "warnings": []
    }
```

## Logs

Cada execucao gera registro em `service_hook_executions`, com status, duracao, mensagens, avisos e erro.

## DB2

A integracao DB2 deve ser implementada dentro das functions ou em conectores chamados por elas. As credenciais devem ficar em variaveis de ambiente ou mecanismo de secrets, nunca no cadastro do hook.

## Seguranca

Codigo Python salvo em banco deve ser tratado como recurso administrativo sensivel. Nesta versao a execucao ocorre dentro do processo Flask, entao somente administradores do sistema devem cadastrar/editar functions. Antes de uso em producao, o recomendado e evoluir para sandbox/processo isolado, limite real de tempo de execucao e lista controlada de imports.
