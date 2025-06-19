from aiogram import Router
from . import user, admin

router = Router()

router.include_routers(
    user.router,
    admin.router,

)