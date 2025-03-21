import logging
from aiogram import Router
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated

logger = logging.getLogger('bot_app.' + __name__)
router = Router()

@router.callback_query()
async def callback_other_handler(callback: CallbackQuery):
    logger.debug(f'callback_other_handler. User_id: {callback.from_user.id}: {callback.data}')
    await callback.answer(callback.data)


@router.message()
async def message_other_handler(message: Message):
    logger.debug(f'message_other_handler. User_id: {message.from_user.id}: {message.text}')
    await message.answer(message.text)


