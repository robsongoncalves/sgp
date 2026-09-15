from urllib.parse import urlsplit

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Documentation, Service
from app.documentation_extractor import extract_documentation_sections
from app.service_description import description_fields

documentations_bp = Blueprint('documentations', __name__)


def serialize(item):
    return {'id': item.id, 'url': item.url, 'description': item.description,
            'sync_enabled': item.sync_enabled,
            'headings': item.headings, **description_fields(item.description)}


def validate(data):
    if not isinstance(data, dict):
        return 'Informe os dados da documentacao.'
    url = data.get('url')
    try:
        parsed = urlsplit(url.strip()) if isinstance(url, str) else None
        if not parsed or parsed.scheme not in ('http', 'https') or not parsed.hostname:
            return 'Informe uma URL HTTP ou HTTPS valida.'
    except ValueError:
        return 'Informe uma URL valida.'
    if not isinstance(data.get('description', ''), str):
        return 'Informe uma descricao em texto ou HTML.'
    if 'sync_enabled' in data and not isinstance(data['sync_enabled'], bool):
        return 'Informe uma flag de sincronizacao valida.'
    headings = data.get('headings', ['DEFINIÇÃO', 'QUEM FAZ?'])
    if not isinstance(headings, list) or not all(isinstance(h, str) for h in headings):
        return 'Informe os topicos como uma lista de textos.'
    return None


@documentations_bp.get('/documentations')
def list_documentations():
    return jsonify([serialize(d) for d in Documentation.query.order_by(Documentation.url, Documentation.id).all()])


@documentations_bp.get('/documentations/<int:item_id>')
def get_documentation(item_id):
    item = db.session.get(Documentation, item_id)
    if item is None:
        return jsonify(message='Documentacao nao encontrada.'), 404
    return jsonify(serialize(item))


@documentations_bp.post('/documentations')
@documentations_bp.put('/documentations/<int:item_id>')
def save_documentation(item_id=None):
    item = db.session.get(Documentation, item_id) if item_id else Documentation()
    if item is None:
        return jsonify(message='Documentacao nao encontrada.'), 404
    data = request.get_json(silent=True) or {}
    error = validate(data)
    if error:
        return jsonify(message=error), 400
    item.url = data['url'].strip()
    item.description = data.get('description', '').strip()
    if 'sync_enabled' in data:
        item.sync_enabled = data['sync_enabled']
    item.headings = list(dict.fromkeys(h.strip() for h in data.get('headings', ['DEFINIÇÃO', 'QUEM FAZ?']) if h.strip()))
    db.session.add(item)
    db.session.commit()
    return jsonify(serialize(item)), 200 if item_id else 201


@documentations_bp.delete('/documentations/<int:item_id>')
def delete_documentation(item_id):
    item = db.session.get(Documentation, item_id)
    if item is None:
        return jsonify(message='Documentacao nao encontrada.'), 404
    if Service.query.filter_by(documentation_id=item_id).first():
        return jsonify(message='Esta documentacao esta vinculada a um servico. Remova o vinculo antes de excluir.'), 409
    try:
        db.session.delete(item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message='Esta documentacao esta em uso.'), 409
    return '', 204


@documentations_bp.post('/documentations/import')
def import_documentation():
    result, error = extract_documentation_sections(request.get_json(silent=True) or {})
    if error:
        return jsonify(message=error), 400
    return jsonify(result)


@documentations_bp.post('/documentations/sync')
def sync_documentations():
    item_ids = [row.id for row in Documentation.query.filter_by(sync_enabled=True).order_by(Documentation.id).all()]
    updated = 0
    errors = []
    for item_id in item_ids:
        item = db.session.get(Documentation, item_id)
        if item is None or not item.sync_enabled:
            continue
        url = item.url
        try:
            result, error = extract_documentation_sections({
                'url': url, 'headings': item.headings, 'output_format': 'html',
            })
            if error or not result or not result.get('description', '').strip():
                errors.append({'id': item_id, 'url': url,
                               'message': error or 'Nenhum conteudo encontrado. Descricao anterior preservada.'})
                continue
            item.description = result['description']
            db.session.commit()
            updated += 1
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Falha ao sincronizar documentacao %s', item_id)
            errors.append({'id': item_id, 'url': url, 'message': 'Nao foi possivel sincronizar esta documentacao.'})
    return jsonify(total=len(item_ids), updated=updated, failed=len(errors), errors=errors)
