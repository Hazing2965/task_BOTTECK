import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



async def create_subscription_keyboard(member_channel = False, member_group = False):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if not member_channel:
        kb_builder.add(InlineKeyboardButton(text='Подписаться на канал', url=os.getenv('CHANNEL_LINK')))
    if not member_group:
        kb_builder.add(InlineKeyboardButton(text='Вступить в группу', url=os.getenv('GROUP_LINK')))

    kb_builder.add(InlineKeyboardButton(text='Проверить', callback_data='check_subscription'))
    
    kb_builder.adjust(1)
    return kb_builder.as_markup()


async def create_payment_keyboard(payment_url: str, payment_id: str):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.add(InlineKeyboardButton(text='Оплатить', url=payment_url))
    kb_builder.add(InlineKeyboardButton(text='Проверить платёж', callback_data=f'check_payment;{payment_id}'))
    
    kb_builder.adjust(1)
    return kb_builder.as_markup()
