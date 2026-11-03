
import calendar
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models
from app.schemas import ContactCreate, ContactUpdate


def get_contacts(db: Session, user_id: int):
    return (
        db.query(models.Contact)
        .filter(models.Contact.user_id == user_id)
        .all()
    )


def get_contact(db: Session, contact_id: int, user_id: int):
    return (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id,
            models.Contact.user_id == user_id,
        )
        .first()
    )


def create_contact(db: Session, contact: ContactCreate, user_id: int):
    db_contact = models.Contact(
        **contact.model_dump(),
        user_id=user_id,
    )

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


def update_contact(
    db: Session,
    db_contact: models.Contact,
    contact: ContactUpdate,
):
    for field, value in contact.model_dump().items():
        setattr(db_contact, field, value)

    db.commit()
    db.refresh(db_contact)

    return db_contact


def delete_contact(db: Session, db_contact: models.Contact):
    db.delete(db_contact)
    db.commit()


def search_contacts(db: Session, query: str, user_id: int):
    search = f"%{query}%"

    return (
        db.query(models.Contact)
        .filter(
            models.Contact.user_id == user_id,
            (
                models.Contact.first_name.ilike(search)
                | models.Contact.last_name.ilike(search)
                | models.Contact.email.ilike(search)
            ),
        )
        .all()
    )


def get_birthday_for_year(birthday: date, year: int) -> date:
    if birthday.month == 2 and birthday.day == 29:
        if not calendar.isleap(year):
            return date(year, 2, 28)

    return birthday.replace(year=year)


def get_upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    end_date = today + timedelta(days=7)

    contacts = (
        db.query(models.Contact)
        .filter(models.Contact.user_id == user_id)
        .all()
    )

    upcoming = []

    for contact in contacts:
        birthday = get_birthday_for_year(
            contact.birthday,
            today.year,
        )

        if birthday < today:
            birthday = get_birthday_for_year(
                contact.birthday,
                today.year + 1,
            )

        if today <= birthday <= end_date:
            upcoming.append(contact)

    return upcoming
