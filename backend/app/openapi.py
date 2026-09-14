from __future__ import annotations


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "SGP API",
        "version": "0.1.0",
        "description": "API do Sistema de Gestao de Processos e Servicos.",
    },
    "servers": [
        {
            "url": "http://localhost:5000/api",
            "description": "Ambiente local",
        }
    ],
    "tags": [
        {"name": "Health"},
        {"name": "Autenticacao"},
        {"name": "Catalogo Publico"},
        {"name": "Usuarios"},
        {"name": "Grupos de Usuarios"},
        {"name": "Categorias de Servico"},
        {"name": "Tipos de Documentos"},
        {"name": "Formularios"},
        {"name": "Modelos de Parecer"},
        {"name": "Functions"},
        {"name": "Logs"},
        {"name": "Servicos"},
        {"name": "Solicitacoes"},
    ],
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Verifica se a API esta online",
                "responses": {"200": {"description": "API online"}},
            }
        },
        "/auth/login": {
            "post": {
                "tags": ["Autenticacao"],
                "summary": "Autentica usuario por email e senha",
                "responses": {"200": {"description": "Usuario autenticado"}},
            }
        },
        "/public/services": {
            "get": {
                "tags": ["Catalogo Publico"],
                "summary": "Lista servicos ativos para o catalogo publico",
                "responses": {"200": {"description": "Servicos publicos retornados"}},
            }
        },
        "/users": {
            "get": {
                "tags": ["Usuarios"],
                "summary": "Lista usuarios",
                "responses": {"200": {"description": "Usuarios retornados"}},
            },
            "post": {
                "tags": ["Usuarios"],
                "summary": "Cria usuario",
                "responses": {"201": {"description": "Usuario criado"}},
            },
        },
        "/users/{user_id}": {
            "get": {
                "tags": ["Usuarios"],
                "summary": "Consulta usuario",
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Usuario retornado"}},
            },
            "put": {
                "tags": ["Usuarios"],
                "summary": "Atualiza usuario",
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Usuario atualizado"}},
            },
            "delete": {
                "tags": ["Usuarios"],
                "summary": "Remove usuario",
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Usuario removido"}},
            },
        },
        "/users/{user_id}/groups": {
            "get": {
                "tags": ["Usuarios"],
                "summary": "Lista grupos associados ao usuario",
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Grupos do usuario retornados"}},
            },
        },
        "/user-groups": {
            "get": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Lista grupos de usuarios",
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {"200": {"description": "Grupos retornados"}},
            },
            "post": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Cria grupo de usuarios",
                "responses": {"201": {"description": "Grupo criado"}},
            },
        },
        "/user-groups/{group_id}": {
            "put": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Atualiza grupo de usuarios",
                "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Grupo atualizado"}},
            },
            "delete": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Remove grupo de usuarios",
                "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Grupo removido"}},
            },
        },
        "/user-groups/{group_id}/members": {
            "get": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Lista membros do grupo",
                "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Membros retornados"}},
            },
            "put": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Atualiza membros do grupo",
                "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Membros atualizados"}},
            },
        },
        "/service-categories": {
            "get": {
                "tags": ["Categorias de Servico"],
                "summary": "Lista categorias de servico",
                "responses": {"200": {"description": "Categorias retornadas"}},
            },
            "post": {
                "tags": ["Categorias de Servico"],
                "summary": "Cria categoria de servico",
                "responses": {"201": {"description": "Categoria criada"}},
            },
        },
        "/service-categories/{category_id}": {
            "put": {
                "tags": ["Categorias de Servico"],
                "summary": "Atualiza categoria de servico",
                "parameters": [{"name": "category_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Categoria atualizada"}},
            },
            "delete": {
                "tags": ["Categorias de Servico"],
                "summary": "Remove categoria de servico",
                "parameters": [{"name": "category_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Categoria removida"}},
            },
        },
        "/document-types": {
            "get": {
                "tags": ["Tipos de Documentos"],
                "summary": "Lista tipos de documentos",
                "responses": {"200": {"description": "Tipos de documentos retornados"}},
            },
            "post": {
                "tags": ["Tipos de Documentos"],
                "summary": "Cria tipo de documento",
                "responses": {"201": {"description": "Tipo de documento criado"}},
            },
        },
        "/document-types/{document_type_id}": {
            "put": {
                "tags": ["Tipos de Documentos"],
                "summary": "Atualiza tipo de documento",
                "parameters": [{"name": "document_type_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Tipo de documento atualizado"}},
            },
            "delete": {
                "tags": ["Tipos de Documentos"],
                "summary": "Remove tipo de documento",
                "parameters": [{"name": "document_type_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Tipo de documento removido"}},
            },
        },
        "/form-templates": {
            "get": {
                "tags": ["Formularios"],
                "summary": "Lista formularios",
                "responses": {"200": {"description": "Formularios retornados"}},
            },
            "post": {
                "tags": ["Formularios"],
                "summary": "Cria formulario",
                "responses": {"201": {"description": "Formulario criado"}},
            },
        },
        "/form-templates/{template_id}": {
            "put": {
                "tags": ["Formularios"],
                "summary": "Atualiza formulario",
                "parameters": [{"name": "template_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Formulario atualizado"}},
            },
            "delete": {
                "tags": ["Formularios"],
                "summary": "Remove formulario",
                "parameters": [{"name": "template_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Formulario removido"}},
            },
        },
        "/opinion-templates": {
            "get": {
                "tags": ["Modelos de Parecer"],
                "summary": "Lista modelos de parecer",
                "responses": {"200": {"description": "Modelos de parecer retornados"}},
            },
            "post": {
                "tags": ["Modelos de Parecer"],
                "summary": "Cria modelo de parecer",
                "responses": {"201": {"description": "Modelo de parecer criado"}},
            },
        },
        "/opinion-templates/{template_id}": {
            "put": {
                "tags": ["Modelos de Parecer"],
                "summary": "Atualiza modelo de parecer",
                "parameters": [{"name": "template_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Modelo de parecer atualizado"}},
            },
            "delete": {
                "tags": ["Modelos de Parecer"],
                "summary": "Remove modelo de parecer",
                "parameters": [{"name": "template_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Modelo de parecer removido"}},
            },
        },
        "/automation-functions": {
            "get": {
                "tags": ["Functions"],
                "summary": "Lista functions de automacao",
                "responses": {"200": {"description": "Functions retornadas"}},
            },
            "post": {
                "tags": ["Functions"],
                "summary": "Cria function de automacao",
                "responses": {"201": {"description": "Function criada"}},
            },
        },
        "/automation-functions/{function_id}": {
            "put": {
                "tags": ["Functions"],
                "summary": "Atualiza function de automacao",
                "parameters": [{"name": "function_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Function atualizada"}},
            },
            "delete": {
                "tags": ["Functions"],
                "summary": "Remove function de automacao",
                "parameters": [{"name": "function_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Function removida"}},
            },
        },
        "/logs/automation": {
            "get": {
                "tags": ["Logs"],
                "summary": "Lista logs de execucao das automacoes",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "default": 300},
                    }
                ],
                "responses": {"200": {"description": "Logs retornados"}},
            }
        },
        "/services": {
            "get": {
                "tags": ["Servicos"],
                "summary": "Lista servicos",
                "responses": {"200": {"description": "Servicos retornados"}},
            },
            "post": {
                "tags": ["Servicos"],
                "summary": "Cria servico",
                "responses": {"201": {"description": "Servico criado"}},
            },
        },
        "/services/{service_id}": {
            "put": {
                "tags": ["Servicos"],
                "summary": "Atualiza servico",
                "parameters": [{"name": "service_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Servico atualizado"}},
            },
            "delete": {
                "tags": ["Servicos"],
                "summary": "Remove servico",
                "parameters": [{"name": "service_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"204": {"description": "Servico removido"}},
            },
        },
        "/service-requests": {
            "get": {
                "tags": ["Solicitacoes"],
                "summary": "Lista solicitacoes",
                "parameters": [
                    {
                        "name": "requester_user_id",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer"},
                    },
                    {
                        "name": "group_id",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer"},
                    },
                    {
                        "name": "service_slug",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "status",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                ],
                "responses": {"200": {"description": "Solicitacoes retornadas"}},
            },
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Cria ou reutiliza solicitacao inicial para um servico",
                "responses": {
                    "200": {"description": "Solicitacao inicial existente reutilizada"},
                    "201": {"description": "Solicitacao criada"},
                },
            },
        },
        "/service-requests/{service_request_id}": {
            "get": {
                "tags": ["Solicitacoes"],
                "summary": "Consulta solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Solicitacao retornada"}},
            },
        },
        "/service-requests/{service_request_id}/form-data": {
            "patch": {
                "tags": ["Solicitacoes"],
                "summary": "Atualiza dados preenchidos da solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "form_data": {"type": "object"},
                                },
                                "required": ["form_data"],
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Dados atualizados"}},
            },
        },
        "/service-requests/{service_request_id}/situation": {
            "patch": {
                "tags": ["Solicitacoes"],
                "summary": "Atualiza situacao de uma solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Situacao atualizada"}},
            },
        },
        "/service-requests/{service_request_id}/documents": {
            "get": {
                "tags": ["Solicitacoes"],
                "summary": "Lista documentos da solicitacao",
                "parameters": [{"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Documentos retornados"}},
            },
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Cria documento da solicitacao",
                "parameters": [{"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"201": {"description": "Documento criado"}},
            },
        },
        "/service-request-documents": {
            "get": {
                "tags": ["Solicitacoes"],
                "summary": "Lista documentos atribuidos ao usuario",
                "parameters": [
                    {"name": "assigned_to_user_id", "in": "query", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Documentos atribuidos retornados"}},
            },
        },
        "/service-requests/{service_request_id}/documents/{document_id}": {
            "put": {
                "tags": ["Solicitacoes"],
                "summary": "Atualiza documento da solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "document_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Documento atualizado"}},
            },
            "delete": {
                "tags": ["Solicitacoes"],
                "summary": "Remove documento da solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "document_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "user_id", "in": "query", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"204": {"description": "Documento removido"}},
            },
        },
        "/service-requests/{service_request_id}/documents/{document_id}/submit": {
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Envia documento para analise",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "document_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Documento enviado"}},
            },
        },
        "/service-requests/{service_request_id}/documents/{document_id}/decision": {
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Registra decisao de documento atribuido",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "document_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Decisao registrada"}},
            },
        },
        "/service-requests/{service_request_id}/documents/{document_id}/attachments": {
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Anexa arquivo a um documento da solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "document_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"201": {"description": "Anexo criado"}},
            },
        },
        "/service-requests/{service_request_id}/attachments": {
            "get": {
                "tags": ["Solicitacoes"],
                "summary": "Lista anexos de uma solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "context_type", "in": "query", "required": False, "schema": {"type": "string"}},
                    {"name": "requirement_code", "in": "query", "required": False, "schema": {"type": "string"}},
                    {"name": "item_index", "in": "query", "required": False, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Anexos retornados"}},
            },
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Envia anexo para uma solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"},
                                    "uploaded_by_user_id": {"type": "integer"},
                                    "context_type": {"type": "string"},
                                    "requirement_code": {"type": "string"},
                                    "item_index": {"type": "integer"},
                                    "description": {"type": "string"},
                                },
                                "required": ["file", "uploaded_by_user_id"],
                            }
                        }
                    },
                },
                "responses": {"201": {"description": "Anexo criado"}},
            },
        },
        "/service-requests/{service_request_id}/attachments/{attachment_id}/download": {
            "get": {
                "tags": ["Solicitacoes"],
                "summary": "Baixa anexo de uma solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "attachment_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Arquivo retornado"}},
            },
        },
        "/service-requests/{service_request_id}/attachments/{attachment_id}": {
            "delete": {
                "tags": ["Solicitacoes"],
                "summary": "Remove anexo de uma solicitacao",
                "parameters": [
                    {"name": "service_request_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "attachment_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {"204": {"description": "Anexo removido"}},
            },
        },
    },
}
