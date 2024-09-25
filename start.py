from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service import AService, ServicesController


class StartService(AService):

    @classmethod
    def init(self, bot: Bot, dispatcher: Dispatcher, controller: ServicesController):
        @dispatcher.message(Command("start"))
        async def cmd_start(message: Message):
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text="О боте",
                callback_data="start_about")
            )

            await message.answer("""
Привет!👋
Это Target бот.
Если вам нужна справка моежте нажать кнопку ниже, или использовать команду /help
Так же можно посмотреть информацию о боте, так же использовал кнопку или команду /about
            """, reply_markup=builder.as_markup())

        @dispatcher.message(Command("about"))
        async def cmd_about(message: Message):
            await message.answer("""
Target bot

Создан @stopmind c ♥
Основан на python, aiogram и pydantic.
Github: https://github.com/stopmind/TargetBot
        """)

        @dispatcher.callback_query(lambda a: a.data == "start_about")
        async def callback_about(callback: CallbackQuery):
            await cmd_about(callback.message)
            await callback.answer()
