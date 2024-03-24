from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal

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
    prefix="/lifts"
)


# class LiftSchemaPost(Schema):
#     weight = fields.Float(required=True)
#     lift_type = fields.Str(
#         required=True,
#         data_key="liftType",
#         validate=validate.OneOf([SQUAT, BENCH, DEADLIFT])
#     )

# class LiftSchemaGet(Schema):
#     lift_type = fields.Str(
#         required=True,
#         validate=validate.OneOf([SQUAT, BENCH, DEADLIFT])
#     )
#     aggregation = fields.Str(
#         required=True,
#         validate=validate.OneOf([PR, LAST, ALL])
#     )

class Lift(BaseModel):
    weight: float
    lift_type: Literal[SQUAT, BENCH, DEADLIFT] = Field(alias="liftType")


@router.get("/squats")
def get_squats(db: Session = Depends(get_db)):
    lifts = db.query(Squat).all()

    return lifts

@router.get("/squats/{user_id}")
def get_user_squats(user_id: int, db: Session = Depends(get_db)):
    lifts = db.query(Squat).filter(Squat.user_id == user_id).all()

    return lifts

@router.get("/benches")
def get_benches(db: Session = Depends(get_db)):
    lifts = db.query(Bench).all()

    return lifts

@router.get("/benches/{user_id}")
def get_user_benches(user_id: int, db: Session = Depends(get_db)):
    lifts = db.query(Bench).filter(Bench.user_id == user_id).all()

    return lifts

@router.get("/deadlifts")
def get_deadlifts(db: Session = Depends(get_db)):
    lifts = db.query(Deadlift).all()

    return lifts

@router.get("/deadlifts/{user_id}")
def get_user_deadlifts(user_id: int, db: Session = Depends(get_db)):
    lifts = db.query(Deadlift).filter(Deadlift.user_id == user_id).all()

    return lifts

@router.get("/{user_id}")
def get_user_lifts(user_id: int, db: Session = Depends(get_db)):
    squats = get_user_squats(user_id=user_id)
    benches = get_user_benches(user_id=user_id)
    deadlifts = get_user_deadlifts(user_id=user_id)

    print(squats)
    print(benches)
    print(deadlifts)

    return {}

@router.post("/{user_id}")
def create_lift(user_id: int, db: Session = Depends(get_db)):
    pass

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
