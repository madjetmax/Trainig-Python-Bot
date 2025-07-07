from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, ChatMemberUpdated, CallbackQuery

from config import *
from keyboards import callback_filters

from typing import Any, Coroutine, Dict, Callable, Awaitable
from cachetools import TTLCache

# for messages, commands
class AdminMessageMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=5)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        
        # message
        if isinstance(event, Message):
            if event.text == "/admin_message":
                if user.id in self.cache:
                    return
                self.cache[user.id] = True
            return await handler(event, data)
            
        # callback
        if isinstance(event, CallbackQuery):
            calldata = data.get("callback_data")
            if isinstance(calldata, callback_filters.UserControllAdminMessage):
                if user.id in self.cache:
                    return
                self.cache[user.id] = True

            return await handler(event, data)
        
        return await handler(event, data)
    
admin_message_middleware = AdminMessageMiddleware()