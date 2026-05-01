from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import schemas.mail as mail_schemas
import models.mail as mail_models
from datetime import datetime

async def get_mails(db: AsyncSession) -> list[mail_models.Mail]:
    """
    Args:
        db (AsyncSession): 非同期セッション
    Returns:
        list[Mail]: メールのリスト
    """
    result = await db.execute(select(mail_models.Mail))
    mails = result.scalars().all()
    return mails


