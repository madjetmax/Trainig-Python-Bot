from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, ChatMemberUpdated, CallbackQuery
from config import *

from typing import Any, Coroutine, Dict, Callable, Awaitable

# for messages, commands
class HandlersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # check if user is admin        
        if event.from_user.id in ADMINS:
            return await handler(event, data)
        return 


# for callbacks
class CallbacksMiddleware(BaseMiddleware):
    # maybe i will use it, but not it's useless :(
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # check if user is admin       
        print(111) 
        if event.from_user.id in ADMINS:
            return await handler(event, data)
        return 

