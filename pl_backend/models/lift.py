from sqlalchemy import Column, Integer, Date, ForeignKey, Float
from datetime import date
from . import Base



class Lift(Base): # Obbligatorio che la classe estenda Base
    __tablename__ = "lifts" # Questo il nome effettivo della tabella nel DB

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Con l'opzione ondelete indichiamo che se il parent viene cancellato, tutti i figli vengono cancellati (quindi se uno user viene cancellato, tutti i suoi pesi vengono cancellati)
    weight = Column(Float, nullable=False)
    registered_dt = Column(Date, default=date.today())

class Squat(Lift):
    pass

class Bench(Lift):
    pass

class Deadlift(Lift):
    pass