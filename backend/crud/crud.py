from backend.models import db, Note, User


def crud_reg(user: User):
        db.session.add(user)
        db.session.commit()
        return user