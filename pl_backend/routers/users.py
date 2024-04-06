from fastapi import APIRouter, status, Response, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import re

from ..dependencies import get_db
from ..models.user import User
from ..utils import hash_pwd, check_user
from ..oauth2 import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

class UserModel(BaseModel):
    email: EmailStr # Il tipo EmailStr controlla in automatico se è una email valida
    password: str

    @validator("password")
    def password_strength(self, v):
        if len(v) < 8:
            raise ValueError("Password should be at least 8 characters")
        if not re.search("[a-z]", v):
            raise ValueError("Password should have at least one lowercase letter")
        if not re.search("[A-Z]", v):
            raise ValueError("Password should have at least one uppercase letter")
        if not re.search("[0-9]", v):
            raise ValueError("Password should have at least one number")
        if not re.search("[_!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password should have at least one special character")

        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    register_dt: datetime

    class Config:
        from_orm = True


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, # user_id è un PATH PARAMETER, e il suo tipo è SEMPRE str. Se però utilizziamo il type hinting (user_id: int), FastAPI è abbastanza intelligente da fare per noi la conversione. E se il valore non può essere convertito gestisce anche l'errore della chiamata restituendo un messaggio con l'errore
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_user(user_id, current_user)

    user = db.query(User).filter(User.id == user_id).first()

    return user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(
    user: UserModel, # FastAPI in automatico fa i controlli con Pydantic visto che abbiamo utilizzato una classe per definire come devono essere i dati passati al body della richiesta, e restituisce in automatico i messaggi di errore se qualcosa non rispetta lo standard
    db: Session = Depends(get_db),
):
    # Nel DB non salviamo la pwd in chiaro, come ci è stata passata, ma la hashamo. Il vantaggio è che l'hash è in una sola direzione. Quindi una volta che la password è stata hashata non possiamo più recuperare il valore orginale. Per fare il check quindi se la pw è corretta in fase di login andare a vedere il codice che gestisce il login
    hashed_password = hash_pwd(user.password)
    user.password = hashed_password

    new_user = User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    check_user(user_id, current_user)

    user = db.query(User).filter(User.id == user_id).first()

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) # Per la delete non si restituisce niente, solo lo status code 204 per indicare che è andato tutto bene e i dati sono stati cancellati
