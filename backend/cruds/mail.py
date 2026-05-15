from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import schemas.mail as mail_schemas
import models.mail as mail_models

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

async def get_mails_by_user_id(db: AsyncSession, user_id: int) -> list[mail_models.Mail]:
    """
    Args:
        db (AsyncSession): 非同期セッション
        user_id (int): ユーザーID
    Returns:
        list[Mail]: ユーザーのメールのリスト
    """
    result = await db.execute(select(mail_models.Mail).where(mail_models.Mail.user_id == user_id))
    mails = result.scalars().all()
    return mails

async def get_mails_by_category(db: AsyncSession, user_id: int, mail_category: str) -> list[mail_models.Mail]:
    """
    Args:
        db (AsyncSession): 非同期セッション
        user_id (int): ユーザーID
        mail_category (str): メールのカテゴリ
    Returns:
        list[Mail]: ユーザーのメールのリスト
    """
    if mail_category not in ["営業", "製造", "その他"]:
        raise ValueError("Invalid mail category")
    result = await db.execute(select(mail_models.Mail).where(
        mail_models.Mail.user_id == user_id,
        mail_models.Mail.category == mail_category
    ))
    mails = result.scalars().all()
    return mails

async def response_mail(
    db: AsyncSession,
    mail: mail_schemas.MailResponseSchema,
) -> mail_models.MailResponse:
    """
    Args:
        db (AsyncSession): 非同期セッション
        mail (MailResponseSchema): メールの情報
    Returns:
        MailResponse: メールの返信
    """
    response = mail_models.MailResponse(
        response_title=mail.response_title,
        response_description=mail.response_description,
        id=mail.id

    )

    db.add(response)
    await db.commit()
    await db.refresh(response)

    return response


