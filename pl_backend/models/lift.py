from sqlalchemy import Column, Integer, Date, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from datetime import date
from . import Base



class Lift(Base): # Obbligatorio che la classe estenda Base
    __tablename__ = "lifts" # Questo il nome effettivo della tabella nel DB

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Con l'opzione ondelete indichiamo che se il parent viene cancellato, tutti i figli vengono cancellati (quindi se uno user viene cancellato, tutti i suoi pesi vengono cancellati)
    lift_type = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    rpe = Column(Float)
    notes = Column(String)
    register_dt = Column(Date, default=date.today())

    owner = relationship("User") # Ci va il nome della classe su cui vogliamo creare la relazione. Quel che succede è che in questa variabile su cui creiamo la relazione abbiamo accesso a tutti i campi della tabella puntata, secondo la foreignKey specificata
