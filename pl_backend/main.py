from fastapi import FastAPI
from pydantic import BaseModel

from .models import Base
from .models.lifts import (
    Squat,
    Bench,
    Deadlift,
)
from .models.user import User
from .models import engine
from .routers import (
    user,
    lift,
)





Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(lift.router)
