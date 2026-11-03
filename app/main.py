from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.contacts import router as contacts_router

app = FastAPI(
    title="Contacts API",
    description="REST API for managing contacts",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(contacts_router)


@app.get("/")
def read_root():
    return {"message": "Contacts API"}