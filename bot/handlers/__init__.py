from aiogram import Router
from . import user

router = Router()

router.include_routers(
    user.router
)