from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..dependencies import get_db




router = APIRouter(
    prefix="/users",
)

class User(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)): # user_id è un PATH PARAMETER, e il suo tipo è SEMPRE str. Se però utilizziamo il type hinting (user_id: int), FastAPI è abbastanza intelligente da fare per noi la conversione. E se il valore non può essere convertito gestisce anche l'errore della chiamata restituendo un messaggio con l'errore
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    return user

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: Session = Depends(get_db)): # FastAPI in automatico fa i controlli con Pydantic visto che abbiamo utilizzato una classe per definire come devono essere i dati passati al body della richiesta, e restituisce in automatico i messaggi di errore se qualcosa non rispetta lo standard
    new_user = User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
