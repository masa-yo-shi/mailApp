from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.mail import MailSchema, MailResponseSchema, ResponseSchema, UserPublic
import cruds.mail as mail_cruds
import cruds.user as user_cruds
import db
from typing import Annotated
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_NAME,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
import models.mail as mail_models

router = APIRouter(tags=["mails"])
auth_router = APIRouter(tags=["auth"])

@auth_router.post("/register", response_model=UserPublic)
async def register_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(db.get_dbsession)
) -> UserPublic:
    username = form_data.username.strip()
    if len(username) < 3 or len(form_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    user = await user_cruds.get_user_by_username(db_session, username)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    new_user = mail_models.User(
        username=username,
        password_hash=get_password_hash(form_data.password),
    )
    created_user = await user_cruds.post_user(db_session, new_user)
    return created_user

@auth_router.post("/login", response_model=ResponseSchema)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(db.get_dbsession),
) -> ResponseSchema:
    username = form_data.username.strip()
    if not username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    user = await authenticate_user(db_session, username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return ResponseSchema(message="ok")

@router.get("/mails", response_model=list[MailSchema])
async def read_user_mails_by_category(
    user_id: Annotated[int, Depends(get_current_user)],
    db_session: AsyncSession = Depends(db.get_dbsession),
    mail_category: str | None = None
) -> list[MailSchema]:
    if mail_category:
        try:
            mails = await mail_cruds.get_mails_by_category(db_session, user_id, mail_category)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return mails
    else:
        try:
            mails = await mail_cruds.get_mails_by_user_id(db_session, user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return mails

@router.get("/mails/{mail_id}", response_model=MailSchema)
async def get_mail_by_id(
    mail_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    db_session: AsyncSession = Depends(db.get_dbsession)
) -> MailSchema:
    try:
        mail = await mail_cruds.get_mail_by_id(db_session, mail_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return mail

@router.post("/mails/{mail_id}/response", response_model=ResponseSchema)
async def response_mail(
    mail_id: int,
    mail_response: MailResponseSchema,
    user_id: Annotated[int, Depends(get_current_user)],
    db_session: AsyncSession = Depends(db.get_dbsession)
) -> ResponseSchema:
    if hasattr(mail_response, "model_copy"):
        resolved_response = mail_response.model_copy(update={"id": mail_id})
    else:
        resolved_response = mail_response.copy(update={"id": mail_id})

    try:
        await mail_cruds.response_mail(db_session, resolved_response)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ResponseSchema(message="ok")