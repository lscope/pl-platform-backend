from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import Base
from .models import engine
from .routers import (
    lifts,
    users,
    auth,
    daily_metrics,
)





Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Accetto chiamate da tutte queste origin
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(lifts.router)
app.include_router(auth.router)
app.include_router(daily_metrics.router)