from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository_users import create_user, get_user_by_email, update_token
from app.schemas import TokenModel, UserCreate, UserLogin,UserResponse
from app.services.auth import auth_service


security = HTTPBearer()
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(body: UserCreate, db: Session=Depends(get_db)):
    existing_user = get_user_by_email(body.email, db)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account with this email already exists",
        )

    user = create_user(body, db)
    return user


@router.post("/login", response_model=TokenModel)
async def login(
    body: UserLogin,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(body.email, db)

    if user is None or not auth_service.verify_password(
        body.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await auth_service.create_access_token(user.email)
    refresh_token = await auth_service.create_refresh_token(user.email)

    update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    email = await auth_service.decode_refresh_token(token)

    user = get_user_by_email(email, db)

    if user is None or user.refresh_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await auth_service.create_access_token(user.email)
    new_refresh_token = await auth_service.create_refresh_token(user.email)

    update_token(user, new_refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
