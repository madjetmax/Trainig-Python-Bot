from aiogram import Router
from . import menu, user_message

router = Router()

router.include_routers(
    menu.router,
    user_message.router
)