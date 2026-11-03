
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import User
from app.schemas import ContactCreate, ContactResponse, ContactUpdate
from app.services.auth import auth_service

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return crud.create_contact(db, contact, current_user.id)


@router.get(
    "/search",
    response_model=list[ContactResponse],
)
def search_contacts(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return crud.search_contacts(db, query, current_user.id)


@router.get(
    "/birthdays",
    response_model=list[ContactResponse],
)
def get_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return crud.get_upcoming_birthdays(db, current_user.id)


@router.get(
    "/",
    response_model=list[ContactResponse],
)
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return crud.get_contacts(db, current_user.id)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = crud.get_contact(db, contact_id, current_user.id)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
)
def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    db_contact = crud.get_contact(db, contact_id, current_user.id)

    if db_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return crud.update_contact(db, db_contact, contact)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    db_contact = crud.get_contact(db, contact_id, current_user.id)

    if db_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    crud.delete_contact(db, db_contact)
