from aiogram import Bot, Dispatcher
from service import AService, ServicesController

class HelpService(AService):
    @classmethod
    def init(self, bot: Bot, dispatcher: Dispatcher, controller: ServicesController):
        pass