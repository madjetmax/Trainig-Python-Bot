from aiogram import Router
from . import register, training, menu, admin_message

router = Router()

router.include_routers(
    register.router,
    training.router,
    menu.router,
    admin_message.router
)