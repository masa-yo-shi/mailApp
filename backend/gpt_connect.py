import json
from typing import Literal
from pydantic import BaseModel
from openai import AsyncOpenAI
from sqlalchemy import select, update
from db import async_session
import models.mail as mail_models

# in = (title, id)
# out= (category, id)

client = AsyncOpenAI()

async def insert_category(user_id: int) -> None:

    class ClassifiedTitle(BaseModel):
        category: Literal["製造", "営業", "その他"]
        id: int

    class ClassificationResult(BaseModel):
        items: list[ClassifiedTitle]
    
    async with async_session() as session:
        stmt = select(mail_models.Mail.title, mail_models.Mail.id).where(
            mail_models.Mail.category == "inbox",
            mail_models.Mail.user_id == user_id,
        )
        result = await session.execute(stmt)
        low_data = [(title, item_id) for title, item_id in result.all()]

        print(f"DEBUG: Fetched {len(low_data)} records from database")
        if low_data:
            print(f"DEBUG: Sample data: {low_data[:3]}")
        else:
            print("DEBUG: No inbox records to classify")
            return

        input_text = json.dumps(
            [{"title": title, "id": item_id} for title, item_id in low_data],
            ensure_ascii=False,
        )

        try:
            response = await client.responses.parse(
                model="gpt-4.1-mini",
                instructions="""
    あなたはタイトル分類器です。
    次のカテゴリのどれか1つだけを返してください:
    製造, 営業, その他

    入力形式：[{'title': '...', 'id': 1}, ...]
    出力形式：{"items": [{"category": "...", "id": 1}, ...]}
    """,
                input=input_text,
                text_format=ClassificationResult,
            )

            parsed = response.output_parsed
            if parsed is None:
                raise ValueError("OpenAI response parsing failed")
            allowed_ids = {item_id for _, item_id in low_data}
            classified_data = [
                (item.category, item.id)
                for item in parsed.items
                if item.id in allowed_ids
            ]
            print(f"DEBUG: Classified {len(classified_data)} records")

            updated_count = 0
            for category, item_id in classified_data:
                await session.execute(
                    update(mail_models.Mail)
                    .where(
                        mail_models.Mail.id == item_id,
                        mail_models.Mail.user_id == user_id,
                    )
                    .values(category=category)
                )
                updated_count += 1
                print(f"Updated mail with id {item_id} to category {category}")

            await session.commit()
            print(f"DEBUG: Successfully committed {updated_count} updates")

            # Verify the updates
            verify_result = await session.execute(
                select(mail_models.Mail.id, mail_models.Mail.category)
                .select_from(mail_models.Mail)
                .where(
                    mail_models.Mail.category.is_not(None),
                    mail_models.Mail.user_id == user_id,
                )
                .limit(10)
            )
            verify = verify_result.fetchall()
            print(f"DEBUG: Verification - Records with category: {verify}")

        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            await session.rollback()
            raise
