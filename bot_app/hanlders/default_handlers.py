import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode

from aio_dialog.states import FaqState, ShopState


logger = logging.getLogger('bot_app.' + __name__)


router = Router()


@router.message(Command('start'))
async def start_command(message: Message, dialog_manager: DialogManager):
    logger.info(f'User_id: {message.from_user.id}: /start command')
    await dialog_manager.start(data={'user_id': message.chat.id}, state=ShopState.main_menu, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND)


@router.message(Command('faq'))
async def faq_command(message: Message, dialog_manager: DialogManager):
    logger.info(f'User_id: {message.from_user.id}: /faq command')
    await dialog_manager.start(
        state=FaqState.faq,
        data={'user_id': message.from_user.id},
        mode=StartMode.RESET_STACK
    )