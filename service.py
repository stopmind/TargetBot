from abc import ABC, abstractmethod
from aiogram import Bot, Dispatcher
from pydantic import BaseModel, ConfigDict


class ServicesController:
    pass

class AService(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def init(cls, bot: Bot, dispatcher: Dispatcher, controller: ServicesController):
        pass


class ServicesController(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    __services: dict[str, AService] = {}
    bot: Bot
    dispatcher: Dispatcher

    def add_service(self, name: str, service: AService):
        self.__services[name] = service
        service.init(self.bot, self.dispatcher, self)

    def get_service[TService: AService](self, name: str) -> TService:
        return self.__services[name]