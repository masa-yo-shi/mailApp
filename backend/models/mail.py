from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Mail(Base):
    __tablename__ = 'mails'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)

    response = relationship("MailResponse", back_populates="mail", uselist=False)

class MailResponse(Base):
    __tablename__ = 'mail_responses'

    id = Column(Integer, ForeignKey("mails.id"), primary_key=True, index=True)
    response_title = Column(String, nullable=False)
    response_description = Column(String, nullable=False)
    
    mail = relationship("Mail", back_populates="response", uselist=False)
