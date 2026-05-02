from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.mail import MailSchema, ResponseSchema, MailResponseSchema
import cruds.mail as mail_cruds
import db

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