from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

from service import AService, ServicesController

class HelpCategory(BaseModel):
    name: str
    text: str

class HelpInfo(BaseModel):
    categories: list[HelpCategory]

class HelpService(AService):
    __help_info: HelpInfo

    @classmethod
    def init(cls, bot: Bot, dispatcher: Dispatcher, controller: ServicesController):
        with open("data/help.json", encoding="utf8") as file:
            cls.__help_info = HelpInfo.model_validate_json(file.read())

        @dispatcher.message(Command("help"))
        async def cmd_help(message: Message):
            builder = InlineKeyboardBuilder()
            builder.max_width = 3
            text = "📜В боте если следющие категории:"

            for i in range(len(cls.__help_info.categories)):
                name = cls.__help_info.categories[i].name
                text = f"{text}\n{name}"
                builder.add(InlineKeyboardButton(
                    text=name,
                    callback_data=f"help_category_{i}")
                )

            await message.answer(text, reply_markup=builder.as_markup())

        @dispatcher.callback_query(lambda a: a.data == "help")
        async def callback_help_category(callback: CallbackQuery):
            await cmd_help(callback.message)
            await callback.answer()

        @dispatcher.callback_query(lambda a: a.data.startswith("help_category_"))
        async def callback_help_category(callback: CallbackQuery):
            category_num = int(callback.data.replace("help_category_", ""))
            category = cls.__help_info.categories[category_num];

            await callback.message.answer(f"{category.name}\n\n{category.text}")
            await callback.answer()