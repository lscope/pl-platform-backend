from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

from ..dependencies import get_db
from ..models.user import User



router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

class UserModel(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")

    class Config:
        allow_population_by_field_name = True

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    register_dt: datetime

    class Config:
        from_orm = True


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)): # user_id è un PATH PARAMETER, e il suo tipo è SEMPRE str. Se però utilizziamo il type hinting (user_id: int), FastAPI è abbastanza intelligente da fare per noi la conversione. E se il valore non può essere convertito gestisce anche l'errore della chiamata restituendo un messaggio con l'errore
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    return user

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserModel, db: Session = Depends(get_db)): # FastAPI in automatico fa i controlli con Pydantic visto che abbiamo utilizzato una classe per definire come devono essere i dati passati al body della richiesta, e restituisce in automatico i messaggi di errore se qualcosa non rispetta lo standard
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
