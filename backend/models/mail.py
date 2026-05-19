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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="mails")
    response = relationship("MailResponse", back_populates="mail", uselist=False)

class MailResponse(Base):
    __tablename__ = 'mail_responses'

    id = Column(Integer, ForeignKey("mails.id"), primary_key=True, index=True)
    response_title = Column(String, nullable=False)
    response_description = Column(String, nullable=False)
    
    mail = relationship("Mail", back_populates="response", uselist=False)

class MailReplyTemplate(Base):
    __tablename__ = 'mail_reply_templates'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_name = Column(String, nullable=False)
    template_title = Column(String, nullable=False)
    template_description = Column(String, nullable=False)

    relationships = relationship("User", back_populates="reply_templates")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    mails = relationship("Mail", back_populates="user")
    reply_templates = relationship("MailReplyTemplate", back_populates="relationships")