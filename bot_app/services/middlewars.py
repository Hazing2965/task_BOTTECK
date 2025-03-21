import logging
import os
from aiogram import BaseMiddleware
from keyboards.callback_markup import create_subscription_keyboard

from database.database import new_user
logger = logging.getLogger('bot_app.' + __name__)


class UserSend(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        user = event.callback_query.from_user if event.callback_query else event.message.from_user if event.message else None
        chat_id = event.callback_query.message.chat.id if event.callback_query else event.message.chat.id if event.message else None
        if chat_id is None or chat_id < 0:
            logger.debug(f'Other_event. {event}')
            return

        if user:
            logger.info(f'User_update. User_id: {user.id}')
            await new_user(user.id)
            
            member_channel = True
            member_group = True

            try:
                member = await event.bot.get_chat_member(os.getenv('CHANNEL_ID'), user.id)
                logger.debug(f'member: {member}')
                if member.status in ['left', 'kicked', 'banned']:
                    member_channel = False
            except Exception as e:
                logger.error(f"Ошибка при проверке подписки на канал {os.getenv('CHANNEL_ID')}: {e}")

            try:
                member = await event.bot.get_chat_member(os.getenv('GROUP_ID'), user.id)
                logger.debug(f'member: {member}')
                if member.status in ['left', 'kicked', 'banned']:
                    member_group = False
            except Exception as e:
                logger.error(f"Ошибка при проверке подписки на группу {os.getenv('GROUP_ID')}: {e}")
            
            if not member_channel or not member_group:
                await event.bot.send_message(user.id, "Для работы с ботом необходимо подписаться на канал и группу.", reply_markup=await create_subscription_keyboard(member_channel, member_group))
                return
            
            return await handler(event, data) 
        else:
            logger.debug(f'Other_event. {event}')
            return
        