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

async def get_mail_by_id(
    db: AsyncSession,
    mail_id: int,
    user_id: int,
) -> mail_models.Mail:
    result = await db.execute(
        select(mail_models.Mail).where(
            mail_models.Mail.id == mail_id,
            mail_models.Mail.user_id == user_id,
        )
    )
    mail = result.scalars().first()
    if mail is None:
        raise ValueError("Mail not found")
    return mail

async def get_response_templates(
    db: AsyncSession,
    user_id: int,
) -> list[mail_models.MailReplyTemplate]:
    query = select(mail_models.MailReplyTemplate).where(
        mail_models.MailReplyTemplate.user_id == user_id
    )
    result = await db.execute(query)
    templates = result.scalars().all()
    return templates

async def create_response_template(
    db: AsyncSession,
    user_id: int,
    template: mail_schemas.MailReplyTemplateCreate,
) -> mail_models.MailReplyTemplate:
    new_template = mail_models.MailReplyTemplate(
        user_id=user_id,
        template_name=template.template_name,
        template_title=template.template_title,
        template_description=template.template_description,
    )

    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)

    return new_template

async def get_user_by_username(
        db : AsyncSession,
        username: str,
) -> mail_models.User | None:
    result = await db.execute(
         select(mail_models.User).where(mail_models.User.username == username)      
)


