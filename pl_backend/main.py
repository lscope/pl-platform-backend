from fastapi import FastAPI
from pydantic import BaseModel

from .models import Base
from .models.lift import Lift
from .models.user import User
from .models import engine
from .routers import (
    lifts,
    users,
    auth,
)





Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(lifts.router)
app.include_router(auth.router)