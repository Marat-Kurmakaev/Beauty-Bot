import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app import db
from app.config import settings
from app.routers.admin import router as admin_router
from app.routers.booking import router as booking_router
from app.routers.start import router as start_router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await db.connect(settings.database_dsn)
    await db.init_schema()

    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(booking_router)
    dp.include_router(admin_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
