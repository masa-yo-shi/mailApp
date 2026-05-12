from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.mail import MailSchema, ResponseSchema, MailResponseSchema
import cruds.mail as mail_cruds
import db
from typing import Annotated
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from schemas.mail import Token, User
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
)



router = APIRouter(tags=["mails"], prefix="/mails")
auth_router = APIRouter(tags=["auth"])


@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(db.get_dbsession),
)-> Token:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/mails/")
async def read_user_mails(
    user_id: Annotated[int, Depends(get_current_user)],
    db_session: AsyncSession = Depends(db.get_dbsession)
) -> list[MailSchema]:
    mails = await mail_cruds.get_mails_by_user_id(db_session, user_id)
    return mails
