from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from . import db



class Lift(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    registered_dt: Mapped[date] = mapped_column(default=date.today())

class Squat(Lift):
    pass

class Bench(Lift):
    pass

class Deadlift(Lift):
    pass