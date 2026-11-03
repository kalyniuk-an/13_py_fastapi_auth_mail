import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in the .env file")

bearer_scheme = HTTPBearer()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class Auth:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_access_token(
        self,
        email: str,
        expires_delta: timedelta = timedelta(minutes=15),
    ) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": email,
            "scope": "access_token",
            "iat": now,
            "exp": now + expires_delta,
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def create_refresh_token(
        self,
        email: str,
        expires_delta: timedelta = timedelta(days=7),
    ) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": email,
            "scope": "refresh_token",
            "iat": now,
            "exp": now + expires_delta,
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def decode_refresh_token(self, refresh_token: str) -> str:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            email = payload.get("sub")
            scope = payload.get("scope")

            if email is None or scope != "refresh_token":
                raise credentials_exception

            return email

        except JWTError:
            raise credentials_exception

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = credentials.credentials

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            email = payload.get("sub")
            scope = payload.get("scope")

            if email is None or scope != "access_token":
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise credentials_exception

        return user


auth_service = Auth()
