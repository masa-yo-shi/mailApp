import os
import asyncio

import db


async def main() -> None:
    # If you want to reset (drop all tables), run with:
    #   MAILAPP_RESET_DB=1 python init_database.py
    reset = os.getenv("MAILAPP_RESET_DB") == "1"
    await db.init_db(seed_sample=True, reset=reset)


if __name__ == "__main__":
    asyncio.run(main())
