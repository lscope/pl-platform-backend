from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from . import db




class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    register_dt: Mapped[date] = mapped_column(default=date.today())