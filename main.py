import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from service import AService, ServicesController


class StartService(AService):

    @classmethod
    def init(self, bot: Bot, dispatcher: Dispatcher, controller: ServicesController):
        @dispatcher.message(Command("start"))
        async def cmd_start(message: Message):
            await message.reply("Привет!")


logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()
controller = ServicesController(bot=bot, dispatcher=dp)

controller.add_service("start", StartService())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())