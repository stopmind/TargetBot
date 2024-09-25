import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from service import ServicesController
from start import StartService

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()
controller = ServicesController(bot=bot, dispatcher=dp)

controller.add_service("start", StartService())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())