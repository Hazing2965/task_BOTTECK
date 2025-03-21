import logging
from aiogram import Bot, Router
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager

from hanlders.default_handlers import start_command

logger = logging.getLogger('bot_app.' + __name__)
router = Router()

@router.error()
async def error_handler(event: ErrorEvent, bot: Bot, dialog_manager: DialogManager):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)

    if event.update.event_type == 'message':
        # user_id = event.update.message.from_user.id
        message = event.update.message
        
        
    elif event.update.event_type == 'callback_query':
        # user_id = event.update.callback_query.from_user.id
        message = event.update.callback_query.message

    
    if message:
        await message.answer('Произошла ошибка. Попробуйте позже.')
        await start_command(message, dialog_manager)
    