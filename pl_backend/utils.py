from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pwd(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(tentative_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(tentative_password, hashed_password)