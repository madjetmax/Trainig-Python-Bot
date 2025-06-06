from aiogram import Router
from . import register, training, menu

router = Router()

router.include_routers(
    register.router,
    training.router,
    menu.router
)