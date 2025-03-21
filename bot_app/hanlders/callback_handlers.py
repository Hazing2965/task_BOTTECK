import logging
from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from yookassa import Payment

from services.payment_services import check_payment_true
from hanlders.default_handlers import start_command

logger = logging.getLogger('bot_app.' + __name__)
router = Router()

@router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    logger.debug(f'User_id: {callback.from_user.id}: {callback.data}')
    await callback.answer("Проверка подписки...")
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await start_command(callback.message, dialog_manager)


@router.callback_query(F.data.split(';')[0] == 'check_payment')
async def check_payment(callback: CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    logger.debug(f'User_id: {callback.from_user.id}: {callback.data}')
    await callback.answer("Проверка платежа...")

    payment_id = callback.data.split(';')[1]
    payment = Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        logger.info(f'User_id: {callback.from_user.id}: Платеж {payment_id} успешно оплачен')
        await check_payment_true(bot,callback.from_user.id, payment)
    else:
        await callback.answer('Нет оплаты')
    
