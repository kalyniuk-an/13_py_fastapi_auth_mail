from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.services.auth import auth_service


def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(body: UserCreate, db: Session) -> User:
    hashed_password = auth_service.get_password_hash(body.password)


    user = User(
        username=body.username,
        email=body.email,
        password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_token(user: User, refresh_token: str | None, db: Session) -> None:
    user.refresh_token = refresh_token
    db.commit()
