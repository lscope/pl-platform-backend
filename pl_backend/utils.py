from fastapi import HTTPException, status
from passlib.context import CryptContext

from .models.user import User



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pwd(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(tentative_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(tentative_password, hashed_password) # La tentative password viene hashata in automatico, non dobbiamo farlo noi

def check_user(user_id: int, current_user: User) -> None:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
