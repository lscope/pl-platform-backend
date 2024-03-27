from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from os import getenv
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel


oaut2_scheme = OAuth2PasswordBearer("login") # Il parametro deve essere l'endpoint dell'url del token. E' quello che abbiamo inserito nel login

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


class TokenModel(BaseModel):
    id: int

def create_access_token(data: dict):
    to_encode = deepcopy(data) # Copiamo i dati passati in input solo per pulizia, e non sovrascriverli

    # Impostiamo la expiration date del token. E' importante mettere il fuso UTC
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM) # Codifichiamo il token, anche se NON è CRYPTATO, tutti lo possono vedere, però solo noi abbiamo la chiave con cui è stato codificato

    return encoded_jwt

def verify_token(token: str, credentials_excpetion: Exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM) # Facciamo la decodifica del token
        id = payload.get("user_id")

        if id is None:
            raise credentials_excpetion

        token_data = TokenModel(id=id) # Questo serve solo per utilizzare il modello pydantic per validare i dati che ci sono stati passati all'interno del token
    except JWTError:
        raise credentials_excpetion

    return token_data

def get_current_user(token: str = Depends(oaut2_scheme)):
    credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return verify_token(token, credentials_exceptions)