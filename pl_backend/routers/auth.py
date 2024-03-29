from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..utils import hash_pwd, verify_pwd
from ..dependencies import get_db
from ..models.user import User
from ..oauth2 import create_access_token, TokenResponse



router = APIRouter(
    tags=["Login"],
)


@router.post("/login", response_model=TokenResponse)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # L'utilizzo di OAuth2PasswordRequestForm effettua in automatico la ricezione delle credenziali, ma in un formato standard, ossia è un dizionario con due chiavi: "username" e "password". Poi nello username viene messa la mail, però dobbiamo ricordarci che dobbiamo usare la chiave username nella query a db per verificare la mail. Inoltre, il body della richiesta non deve essere sottoforma di json ma di form-data.
    user = db.query(User).filter(User.email == user_credentials.username).first() # first() perché tanto non ci possono essere mail duplicate, quindi prendiamo subito la prima e non sprechiamo risorse del db

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials") #! Non specifichiamo che l'errore è nella mail, perché se é qualcuno che sta tentando di entrare con le credenziali di qualcun altro gli agevoleremmo il lavoro

    # Se l'utente è stato trovato, verifichiamo che la password sia corretta
    # Per verificare che la pw sia corretta, dal momento che l'abbiamo hashata sul db non possiamo più recuperare quella originale, quindi per verificarlo seguiamo questi step:
    #   1) confrontiamo la password hashata a db con la password inserita nel form di login (questa pw deve essere così come ci è stata passata, ci penserà la libreria sotto a confrontarla con quella hashata)
    if not verify_pwd(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials") # Anche qui non diamo indicazione sul fatto che è la password ad essere sbagliata

    # Generazione JWT token
    access_token = create_access_token({"user_id": user.id}) # Siamo noi a decidere quali sono i dati da passare all'interno del token. In questo caso inviamo unicamente l'id, ma avremmo potuto mandare qualsiasi altra cosa

    return {
        "access_token": access_token,
        "token_type": "bearer", # Questo va messo così, è il tipo di questo token
    }