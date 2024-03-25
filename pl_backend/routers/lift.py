from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal, List

from ..models.lifts import Squat, Bench, Deadlift
from ..dependencies import get_db


SQUAT = "squat"
BENCH = "bench"
DEADLIFT = "deadlift"

PR = "PR"
LAST = "last"
ALL = "all"

LIFT_CLASSES = {
    SQUAT: Squat,
    BENCH: Bench,
    DEADLIFT: Deadlift,
}

router = APIRouter(
    prefix="/lifts",
    tags=["Lifts"],
)



class LiftModel(BaseModel):
    weight: float
    lift_type: Literal[SQUAT, BENCH, DEADLIFT] = Field(alias="liftType")

    class Config:
        allow_population_by_field_name = True

class LiftResponse(BaseModel):
    id: int
    user_id: int
    weight: float
    registered_dt: datetime

    class Config:
        from_orm = True


@router.get("/squats", response_model=List[LiftResponse])
def get_squats(db: Session = Depends(get_db)):
    lifts = db.query(Squat).all()

    return lifts

@router.get("/squats/{user_id}", response_model=List[LiftResponse])
def get_user_squats(user_id: int, db: Session = Depends(get_db)):
    lifts = db.query(Squat).filter(Squat.user_id == user_id).all()

    return lifts

@router.get("/benches", response_model=List[LiftResponse])
def get_benches(db: Session = Depends(get_db)):
    lifts = db.query(Bench).all()

    return lifts

@router.get("/benches/{user_id}", response_model=List[LiftResponse])
def get_user_benches(user_id: int, db: Session = Depends(get_db)):
    lifts = db.query(Bench).filter(Bench.user_id == user_id).all()

    return lifts

@router.get("/deadlifts", response_model=List[LiftResponse])
def get_deadlifts(db: Session = Depends(get_db)):
    lifts = db.query(Deadlift).all()

    return lifts

@router.get("/deadlifts/{user_id}", response_model=List[LiftResponse])
def get_user_deadlifts(user_id: int, db: Session = Depends(get_db)):
    lifts = db.query(Deadlift).filter(Deadlift.user_id == user_id).all()

    return lifts

@router.get("/{user_id}", response_model=List[LiftResponse])
def get_user_lifts(user_id: int, db: Session = Depends(get_db)):
    squats = get_user_squats(user_id=user_id)
    benches = get_user_benches(user_id=user_id)
    deadlifts = get_user_deadlifts(user_id=user_id)

    print(squats)
    print(benches)
    print(deadlifts)

    return {}

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED, response_model=LiftResponse)
def create_lift(user_id: int, lift: LiftModel, db: Session = Depends(get_db)):
    lift_model = LIFT_CLASSES[lift.lift_type]

    new_lift = lift_model(
        user_id=user_id,
        **lift.model_dump(),
    )

    db.add(new_lift)
    db.commit()
    db.refresh(new_lift)

    return new_lift

# class LiftResource(Resource):
#     def get(self, user_id):
#         try:
#             data = LiftSchemaGet().load(request.args)
#         except ValidationError as e:
#             return {
#                 "message": str(e),
#             }, 400

#         lift_type = data["lift_type"]
#         aggregation = data["aggregation"]
#         lift_model = LIFT_CLASSES[lift_type] # Determina il modello in base al tipo di alzata

#         # Recupera i dati in base al tipo di aggregazione
#         if aggregation == ALL:
#             lifts = lift_model.query.filter(lift_model.user_id == user_id).all()

#             return {"lifts": [lift.to_json() for lift in lifts]}
#         elif aggregation == PR:
#             lift = lift_model.query.filter(lift_model.user_id == user_id).order_by(lift_model.weight.desc()).first()

#             return lift.to_json() if lift else ({"message": "Nessun record trovato"}, 404)
#         elif aggregation == LAST:
#             lift = lift_model.query.filter(lift_model.user_id == user_id).order_by(lift_model.registered_dt.desc()).first()

#             return lift.to_json() if lift else ({"message": "Nessun record trovato"}, 404)

#     def post(self, user_id):
#         try:
#             data = LiftSchemaPost().load(request.get_json())
#         except ValidationError as e:
#             return {
#                 "message": str(e),
#             }, 400

#         weight = data.get("weight")
#         lift_type = data.get("lift_type")
#         lift_model = LIFT_CLASSES[lift_type] # Determina il modello in base al tipo di alzata

#         lift = lift_model(
#             user_id=user_id,
#             weight=weight,
#         )

#         try:
#             db.session.add(lift)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()

#             return {
#                 "message": "Failed to add new lift",
#                 "error": str(e),
#             }, 500

#         return {"message": f"Added {weight}kg {lift_type} for user {user_id}"}
