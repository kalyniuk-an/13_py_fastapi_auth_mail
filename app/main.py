from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter

from app.routes.auth import router as auth_router
from app.routes.contacts import router as contacts_router
from app.routes.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        encoding="utf-8",
        decode_responses=True,
    )

    await FastAPILimiter.init(redis)

    yield

    await FastAPILimiter.close()


app = FastAPI(
    title="Contacts API",
    description="REST API for managing contacts",
    version="1.0.0",
    lifespan=lifespan,
)

origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(users_router)


@app.get("/")
def read_root():
    return {"message": "Contacts API"}
