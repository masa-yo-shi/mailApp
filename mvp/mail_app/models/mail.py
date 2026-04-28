from sqlalchemy import Column, Integer, String, DateTime
from db import Base

class Mail(Base):
    __tablename__ = 'mails'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)