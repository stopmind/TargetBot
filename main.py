import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from help import HelpService
from minigames import MiniGamesService
from service import ServicesController
from start import StartService

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()
controller = ServicesController(bot=bot, dispatcher=dp)

controller.add_service("start", StartService())
controller.add_service("help", HelpService())
controller.add_service("minigames", MiniGamesService())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())