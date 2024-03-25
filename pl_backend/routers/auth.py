from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..utils import hash_pwd, verify_pwd
from ..dependencies import get_db
from ..models.user import User



router = APIRouter(
    tags=["Login"],
)

class LoginUserModule(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(user_infos: LoginUserModule, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_infos.email).first() # first() perché tanto non ci possono essere mail duplicate, quindi prendiamo subito la prima e non sprechiamo risorse del db

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials") #! Non specifichiamo che l'errore è nella mail, perché se é qualcuno che sta tentando di entrare con le credenziali di qualcun altro gli agevoleremmo il lavoro

    # Se l'utente è stato trovato, verifichiamo che la password sia corretta
    # Per verificare che la pw sia corretta, dal momento che l'abbiamo hashata sul db non possiamo più recuperare quella originale, quindi per verificarlo seguiamo questi step:
    #   1) hashamo la password che ci hanno fornito in fase di login (chiamata anche `tentative password`)
    #   2) confrontiamo la password hashata a db con la password hashata al punto 1
    if not verify_pwd(hash_pwd(user_infos.password), user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials") # Anche qui non diamo indicazione sul fatto che è la password ad essere sbagliata

    # Generazione JWT token
    # Restituizione token

    return {"token": "example token"}