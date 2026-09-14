from __future__ import annotations

from datetime import datetime


def importar_dados_calculadora(context: dict) -> dict:
    user = context["user"]
    config = context.get("config", {})
    siape = str(user.get("siape") or "").strip()

    if not siape:
        return {
            "warnings": ["Usuario sem SIAPE; importacao automatica nao executada."],
        }

    periodo_meses = int(config.get("periodo_meses", 24))
    connection = str(config.get("connection", "db2_guri"))

    # Primeira versao: simula a fonte externa mantendo o contrato que sera usado pelo DB2.
    return {
        "form_data_patch": {
            "automacoes": {
                "progressao_docente.importar_dados_calculadora": {
                    "connection": connection,
                    "siape": siape,
                    "periodo_meses": periodo_meses,
                    "executed_at": datetime.utcnow().isoformat(),
                    "source": "mock",
                }
            },
            "pontuacao": {
                "importados": {
                    "encargos_didaticos": {
                        "siape": siape,
                        "periodo_meses": periodo_meses,
                        "quantidade_horas_aula_semanais_media": 0,
                        "origem": connection,
                        "status": "pendente_integracao_db2",
                    }
                }
            },
        },
        "messages": ["Contexto da calculadora preparado para importacao por SIAPE."],
    }
