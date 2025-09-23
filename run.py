from aiogram import Bot, Dispatcher
import logging
import asyncio
from config import TOKEN
from smth228.app.handlers import router


async def main():
    while True:
        try:
            bot = Bot(token=TOKEN)
            dp = Dispatcher()
            dp.include_router(router)
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Ошибка: {e}. Перезапуск через 5 сек...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
