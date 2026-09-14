from __future__ import annotations

from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models import Service, ServiceRating, User
from app.repositories.utils import datetime_to_api, optional_int


class ServiceRatingsRepository:
    def summary(self, service_id: int, user_id: int | None = None) -> tuple[dict | None, str | None]:
        service = db.session.get(Service, service_id)

        if service is None:
            return None, "Servico nao encontrado."

        average, count = db.session.query(
            func.avg(ServiceRating.rating),
            func.count(ServiceRating.id),
        ).filter(ServiceRating.service_id == service_id).one()

        comments = ServiceRating.query.filter(
            ServiceRating.service_id == service_id,
            ServiceRating.comment != "",
        ).order_by(
            ServiceRating.updated_at.desc(),
            ServiceRating.id.desc(),
        ).limit(10).all()

        user_rating = None
        if user_id is not None:
            rating = ServiceRating.query.filter(
                ServiceRating.service_id == service_id,
                ServiceRating.user_id == user_id,
            ).first()
            user_rating = self._to_dict(rating) if rating else None

        return {
            "service_id": service_id,
            "average_rating": round(float(average or 0), 1),
            "rating_count": int(count or 0),
            "user_rating": user_rating,
            "comments": [self._to_dict(comment) for comment in comments],
        }, None

    def upsert(self, service_id: int, data: dict) -> tuple[dict | None, str | None]:
        service = db.session.get(Service, service_id)
        user_id = optional_int(data.get("user_id"))

        if service is None:
            return None, "Servico nao encontrado."

        if user_id is None or db.session.get(User, user_id) is None:
            return None, "Usuario nao encontrado."

        try:
            rating_value = int(data.get("rating"))
        except (TypeError, ValueError):
            return None, "Informe uma avaliacao valida."

        if rating_value < 1 or rating_value > 5:
            return None, "A avaliacao deve estar entre 1 e 5 estrelas."

        comment = str(data.get("comment", "") or "").strip()
        if len(comment) > 1000:
            return None, "Comentario deve ter no maximo 1000 caracteres."

        rating = ServiceRating.query.filter(
            ServiceRating.service_id == service_id,
            ServiceRating.user_id == user_id,
        ).first()

        if rating is None:
            rating = ServiceRating(service_id=service_id, user_id=user_id)
            db.session.add(rating)

        rating.rating = rating_value
        rating.comment = comment
        rating.updated_at = datetime.utcnow()
        db.session.commit()

        return self._to_dict(rating), None

    def _to_dict(self, rating: ServiceRating) -> dict:
        return {
            "id": rating.id,
            "service_id": rating.service_id,
            "user_id": rating.user_id,
            "user_name": rating.user.name if rating.user else "",
            "rating": rating.rating,
            "comment": rating.comment,
            "created_at": datetime_to_api(rating.created_at),
            "updated_at": datetime_to_api(rating.updated_at),
        }


service_ratings_repository = ServiceRatingsRepository()
