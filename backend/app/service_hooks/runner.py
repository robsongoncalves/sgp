from __future__ import annotations

from copy import deepcopy
from importlib import import_module
from time import perf_counter
from typing import Any

from app.extensions import db
from app.models import Service, ServiceHook, ServiceHookExecution, ServiceRequest, User
from app.repositories.utils import datetime_to_api


class ServiceHookRunner:
    def run(
        self,
        event_name: str,
        service: Service,
        user: User,
        service_request: ServiceRequest | None = None,
        form_data: dict | None = None,
    ) -> dict:
        state = deepcopy(form_data or {})
        hooks = ServiceHook.query.filter(
            ServiceHook.service_id == service.id,
            ServiceHook.event_name == event_name,
            ServiceHook.active.is_(True),
        ).order_by(
            ServiceHook.execution_order.asc(),
            ServiceHook.id.asc(),
        ).all()

        messages: list[str] = []
        warnings: list[str] = []

        for hook in hooks:
            result = self._run_hook(hook, service, user, service_request, event_name, state)
            state = self._deep_merge(state, result.get("form_data_patch", {}))
            messages.extend(str(message) for message in result.get("messages", []))
            warnings.extend(str(warning) for warning in result.get("warnings", []))

        return {
            "form_data": state,
            "messages": messages,
            "warnings": warnings,
        }

    def _run_hook(
        self,
        hook: ServiceHook,
        service: Service,
        user: User,
        service_request: ServiceRequest | None,
        event_name: str,
        form_data: dict,
    ) -> dict[str, Any]:
        started_at = perf_counter()
        status = "success"
        messages: list[str] = []
        warnings: list[str] = []
        error_message = ""
        handler_label = hook.function.slug if hook.function else hook.handler_key

        try:
            if hook.function and not hook.function.active:
                warnings = [f"Function {hook.function.slug} esta inativa."]
                return {
                    "form_data_patch": {},
                    "messages": [],
                    "warnings": warnings,
                }

            handler = (
                self._load_dynamic_handler(hook.function.source_code)
                if hook.function
                else self._load_handler(hook.handler_key)
            )
            context = self._build_context(hook, service, user, service_request, event_name, form_data)
            result = handler(context) or {}

            if not isinstance(result, dict):
                raise ValueError("Handler deve retornar um dicionario.")

            messages = [str(message) for message in result.get("messages", [])]
            warnings = [str(warning) for warning in result.get("warnings", [])]
            return result
        except Exception as exc:  # noqa: BLE001 - loga falha sem derrubar a criacao do servico.
            status = "error"
            error_message = str(exc)
            warnings = [f"Automacao {handler_label} falhou: {error_message}"]
            return {
                "form_data_patch": {},
                "messages": messages,
                "warnings": warnings,
            }
        finally:
            duration_ms = int((perf_counter() - started_at) * 1000)
            db.session.add(
                ServiceHookExecution(
                    hook_id=hook.id,
                    service_request_id=service_request.id if service_request else None,
                    user_id=user.id,
                    event_name=event_name,
                    status=status,
                    duration_ms=duration_ms,
                    messages=messages,
                    warnings=warnings,
                    error_message=error_message,
                )
            )

    def _load_handler(self, handler_key: str):
        module_name, function_name = handler_key.rsplit(".", 1)
        module = import_module(f"app.service_hooks.handlers.{module_name}")
        return getattr(module, function_name)

    def _load_dynamic_handler(self, source_code: str):
        namespace: dict[str, Any] = {}
        exec(source_code, namespace)  # noqa: S102 - execucao dinamica definida por administradores do sistema.
        handler = namespace.get("handle")

        if not callable(handler):
            raise ValueError("Function deve declarar handle(context).")

        return handler

    def _build_context(
        self,
        hook: ServiceHook,
        service: Service,
        user: User,
        service_request: ServiceRequest | None,
        event_name: str,
        form_data: dict,
    ) -> dict:
        return {
            "event": event_name,
            "service": {
                "id": service.id,
                "name": service.name,
                "slug": service.slug,
                "module_key": service.module_key,
            },
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "siape": user.siape,
                "cargo": user.cargo,
                "classe_nivel": user.classe_nivel,
                "local_exercicio": user.local_exercicio,
                "telefone": user.telefone,
            },
            "request": {
                "id": service_request.id if service_request else None,
                "number": service_request.number if service_request else None,
                "status": service_request.status if service_request else None,
                "form_data": form_data,
                "created_at": datetime_to_api(service_request.created_at) if service_request else None,
                "updated_at": datetime_to_api(service_request.updated_at) if service_request else None,
            },
            "config": hook.config or {},
        }

    def _deep_merge(self, base: dict, patch: dict) -> dict:
        if not isinstance(patch, dict):
            return base

        merged = deepcopy(base)

        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value

        return merged


service_hook_runner = ServiceHookRunner()
