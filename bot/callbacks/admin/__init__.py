from aiogram import Router
from . import menu
router = Router()

router.include_routers(
    menu.router
)