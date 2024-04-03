from sqlalchemy import Column, Date, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date

from . import Base



class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    register_dt = Column(Date, default=date.today())
    body_weight = Column(Float)
    calories = Column(Integer)
    hydration = Column(Float) # Litri di acqua
    steps = Column(Integer)
    sleeping_hours = Column(Float)
    sleeping_quality = Column(String)

    user = relationship("User")
