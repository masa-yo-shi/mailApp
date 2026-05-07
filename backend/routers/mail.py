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
    authenticate_user,
    create_access_token,
    get_current_active_user,
)



router = APIRouter(tags=["mails"], prefix="/mails")

# メールの取得
@router.get("/", response_model=list[MailSchema])
async def get_mails(db: AsyncSession = Depends(db.get_dbsession)):
    mails = await mail_cruds.get_mails(db)
    return mails

@router.post("/", response_model=ResponseSchema)
async def response_mail(mail:MailResponseSchema, db:AsyncSession= Depends(db.get_dbsession)):
    response = await mail_cruds.response_mail(db, mail)
    return ResponseSchema(message=f"Mail response created with id {response.id}")

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(db.get_dbsession),
)-> Token:
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
)-> User:
    return current_user

@router.get("/users/me/items/")
async def read_user_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user.items
