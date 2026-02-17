from app.domain.repositories.audit_repo import AuditRepository
from app.domain.entities.audit import Audit
from app.infrastructure.persistence.models.audit_model import AuditModel
from app import db

class SqlAlchemyAuditRepository(AuditRepository):

    def add(self, audit):
        model = AuditModel(
            id=audit.id,
            user_id=audit.user_id,
            message=audit.message,
            date_created=audit.date_created,
        )
        db.session.add(model)
        db.session.commit()

    def count(self):
        return AuditModel.query.count()

    def delete_oldest(self, number_to_delete):
        oldest = (
            AuditModel.query
            .order_by(AuditModel.date_created.asc())
            .limit(number_to_delete)
            .all()
        )

        for record in oldest:
            db.session.delete(record)

        db.session.commit()

    def list(self, page, per_page, user_id=None, search=None):
#        query = AuditModel.query.order_by(AuditModel.date_created.desc())
        query = (
            db.session.query(AuditModel)
            .outerjoin(AuditModel.user)
            .order_by(AuditModel.date_created.desc())
        )

        if user_id:
            query = query.filter(AuditModel.user_id == user_id)

        if search:
            query = query.filter(AuditModel.message.ilike(f"%{search}%"))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        entities = [
            Audit(
                id=m.id,
                user_id=m.user_id,
                username=m.user.username if m.user else None,
                message=m.message,
                date_created=m.date_created,
            )
            for m in pagination.items
        ]

        return entities, pagination

