from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import date
from . import Base



class Lift(Base):
    __tablename__ = "lifts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    registered_dt = Column(Date, default=date.today())

class Squat(Lift):
    pass

class Bench(Lift):
    pass

class Deadlift(Lift):
    pass