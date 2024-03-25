from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..utils import hash_pwd, verify_pwd
from ..dependencies import get_db



router = APIRouter(
    tags=["Login"],
)

class LoginUserModule(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(infos: LoginUserModule, db: Session = Depends(get_db)):
    pass
