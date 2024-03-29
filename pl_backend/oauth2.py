from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from os import getenv
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel


oaut2_scheme = OAuth2PasswordBearer("login") # Il parametro deve essere l'endpoint dell'url che genererà il token. E' quello che abbiamo inserito nel login.

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


class TokenModel(BaseModel):
    id: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = deepcopy(data) # Copiamo i dati passati in input solo per pulizia, e non sovrascriverli

    # Impostiamo la expiration date del token. E' importante mettere il fuso UTC
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Questa è una chiave che va creata così

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM) # Codifichiamo il token, anche se NON è CRYPTATO, tutti lo possono vedere, però solo noi abbiamo la chiave con cui è stato codificato

    return encoded_jwt

def verify_token(token: str, credentials_excpetion: Exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM) # Facciamo la decodifica del token
        id = payload.get("user_id")

        if id is None:
            raise credentials_excpetion

        token_data = TokenModel(id=id) # Questo serve solo per utilizzare il modello pydantic per validare i dati che ci sono stati passati all'interno del token. Il dato che verifichiamo ovviamente dipende dai dati che abbiamo deciso di inserire nel token
    except JWTError:
        raise credentials_excpetion

    return token_data

def get_current_user(token: str = Depends(oaut2_scheme)): # Quello che fa oaut2_scheme (che è una funzione, perché è un'istanza della classe OAuth2PasswordBearer, ma è anche un callable) è andare nell'header della richiesta e cercare l'header Authorization, nel quale ci deve essere il token scritto così: `Bearer <your_token>`, e restituisce il token come stringa. Quindi noi non dobbiamo fare nulla, nessun controllo se il token esiste o è nel formato corretto, fa tutto lui. L'importante è che nell'header della richiesta ci venga passato correttamente
    credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}) # L'header l'ho trovato sulla documentazione di FastAPI

    return verify_token(token, credentials_exceptions)
