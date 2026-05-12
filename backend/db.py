import os
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "mail.sqlite")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_dbsession():
    async with async_session() as session:
        yield session


async def init_db(*, seed_sample: bool, reset: bool) -> None:
    """Create tables and (optionally) seed sample data.

    Notes:
    - Keep this logic out of module top-level to avoid circular-import issues.
    - Uses AsyncEngine/AsyncSession consistently.
    """

    # Ensure all models are imported and registered on Base.metadata
    import models.mail  # noqa: F401

    async with engine.begin() as conn:
        if reset:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    if not seed_sample:
        return

    from models.mail import Mail, User

    async with async_session() as session:
        mail_count = await session.scalar(select(func.count(Mail.id)))
        user_count = await session.scalar(select(func.count(User.id)))

        to_add = []
        if (mail_count or 0) == 0:
            to_add.extend(_sample_mails())
        if (user_count or 0) == 0:
            to_add.extend(_sample_users())

        if to_add:
            session.add_all(to_add)
            await session.commit()


def _sample_mails():
    # Import here to avoid import cycles (models import Base from this module)
    from models.mail import Mail

    return [
        Mail(
            title="見積依頼（サンプル）: 部品A 100個",
            description="部品Aを100個発注したいです。納期と概算見積をご連絡ください。",
            created_at=datetime(2026, 4, 1, 9, 0, 0),
            category="inbox",
            user_id=1,
        ),
        Mail(
            title="納期確認（サンプル）: 4月分の出荷について",
            description="4月中の出荷予定日を確認したいです。可能なら前倒し可否も教えてください。",
            created_at=datetime(2026, 4, 2, 10, 30, 0),
            category="inbox",
            user_id=1,
        ),
        Mail(
            title="図面送付（サンプル）: 改訂版PDF",
            description="改訂版の図面PDFを添付します。差分は2ページ目の寸法のみです。",
            created_at=datetime(2026, 4, 3, 15, 10, 0),
            category="inbox",
            user_id=1,
        ),
        Mail(
            title="請求書（サンプル）: 2026-04",
            description="2026年4月分の請求書です。ご確認ください。",
            created_at=datetime(2026, 4, 5, 11, 45, 0),
            category="その他",
            user_id=1,
        ),
        Mail(
            title="問い合わせ（サンプル）: 製品仕様について",
            description="製品仕様と対応温度範囲について教えてください。",
            created_at=datetime(2026, 4, 10, 14, 5, 0),
            category="inbox",
            user_id=2,
        ),
        Mail(
            title="クレーム（サンプル）: 梱包破損のご連絡",
            description="到着時に梱包が破損していました。写真を添付します。対応をお願いします。",
            created_at=datetime(2026, 4, 12, 16, 40, 0),
            category="inbox",
            user_id=2,
        ),
        Mail(
            title="定例打合せ（サンプル）: 次回アジェンダ",
            description="次回の定例打合せのアジェンダ案です。追記があれば返信ください。",
            created_at=datetime(2026, 4, 15, 13, 0, 0),
            category="その他",
            user_id=2,
        ),
    ]


def _sample_users():
    from models.mail import User
    from pwdlib import PasswordHash

    password_hash = PasswordHash.recommended()

    return [
        User(
            id=1,
            username="johndoe",
            password_hash=password_hash.hash("secret"),
        ),
        User(
            id=2,
            username="testuser",
            password_hash=password_hash.hash("testpassword"),
        ),
    ]