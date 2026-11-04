
from fastapi import Depends, Request, Response
from fastapi_limiter.depends import RateLimiter

from app.models import User
from app.services.auth import auth_service


async def user_identifier(request: Request) -> str:
    user_id = request.state.rate_limit_user_id
    return f"user:{user_id}"


contact_create_limiter = RateLimiter(
    times=5,
    minutes=1,
    identifier=user_identifier,
)


async def rate_limit_by_user(
    request: Request,
    response: Response,
    current_user: User = Depends(auth_service.get_current_user),
):
    request.state.rate_limit_user_id = current_user.id

    await contact_create_limiter(request, response)
