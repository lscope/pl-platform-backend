from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List

from ..dependencies import get_db
from ..models.user import User
from ..utils import hash_pwd


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

class UserModel(BaseModel):
    email: EmailStr # Il tipo EmailStr controlla in automatico se è una email valida
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
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
    # Nel DB non salviamo la pwd in chiaro, come ci è stata passata, ma la hashamo. Il vantaggio è che l'hash è in una sola direzione. Quindi una volta che la password è stata hashata non possiamo più recuperare il valore orginale. Per fare il check quindi se la pw è corretta in fase di login andare a vedere il codice che gestisce il login
    hashed_password = hash_pwd(user.password)
    user.password = hashed_password

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

    return Response(status_code=status.HTTP_204_NO_CONTENT) # Per la delete non si restituisce niente, solo lo status code 204 per indicare che è andato tutto bene e i dati sono stati cancellati
