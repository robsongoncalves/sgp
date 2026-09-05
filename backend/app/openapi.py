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
        {"name": "Usuarios"},
        {"name": "Grupos de Usuarios"},
        {"name": "Categorias de Servico"},
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
        "/user-groups": {
            "get": {
                "tags": ["Grupos de Usuarios"],
                "summary": "Lista grupos de usuarios",
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
                    }
                ],
                "responses": {"200": {"description": "Solicitacoes retornadas"}},
            },
            "post": {
                "tags": ["Solicitacoes"],
                "summary": "Cria solicitacao para um servico",
                "responses": {"201": {"description": "Solicitacao criada"}},
            },
        },
    },
}

