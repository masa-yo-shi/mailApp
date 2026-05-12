import sqlite3
import os
import json
from typing import Literal
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy import select, update
from db import session
import models

db_path = os.path.join(os.path.dirname(__file__), "mail.sqlite")
# con = sqlite3.connect(db_path)
# cur = con.cursor()

# res = cur.execute("SELECT title, id FROM mails WHERE category = 'inbox'")

# in = (title, id)
# out= (category, id)


class ClassifiedTitle(BaseModel):
    category: Literal["製造", "営業", "その他"]
    id: int


class ClassificationResult(BaseModel):
    items: list[ClassifiedTitle]

client = OpenAI()

stmt = select(models.Mail.title, models.Mail.id).where(models.Mail.category == 'inbox')
result = session.scalars(stmt)

low_data = [(row.title, row.id) for row in result]
print(f"DEBUG: Fetched {len(low_data)} records from database")
if low_data:
    print(f"DEBUG: Sample data: {low_data[:3]}")
else:
    print("DEBUG: No inbox records to classify")
    session.close()
    raise SystemExit(0)

input_text = json.dumps(
    [{"title": title, "id": item_id} for title, item_id in low_data],
    ensure_ascii=False,
)

try:
    response = client.responses.parse(
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
    
    classified_data = [(item.category, item.id) for item in response.output_parsed.items]
    print(f"DEBUG: Classified {len(classified_data)} records")
    
    updated_count = 0
    for category, item_id in classified_data:
        session.execute(
            update(models.Mail).where(models.Mail.id == item_id).values(category=category)
        )
        updated_count += 1
        print(f"Updated mail with id {item_id} to category {category}")
    
    session.commit()
    print(f"DEBUG: Successfully committed {updated_count} updates")
    
    # Verify the updates
    verify = session.execute("SELECT id, category FROM mails WHERE category IS NOT NULL LIMIT 5").fetchall()
    print(f"DEBUG: Verification - Records with category: {verify}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    session.rollback()
finally:
    session.close()
    print("Database connection closed")