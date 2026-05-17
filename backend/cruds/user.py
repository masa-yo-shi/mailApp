from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models.mail as mail_models


async def get_user_by_username(
    db: AsyncSession,
    username: str,
) -> mail_models.User | None:
    result = await db.execute(
        select(mail_models.User).where(mail_models.User.username == username)
    )
    return result.scalars().first()

async def post_user(
    db: AsyncSession,
    user: mail_models.User
):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user