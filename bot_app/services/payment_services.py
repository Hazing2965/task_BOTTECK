from decimal import Decimal
import os
import uuid
from aiogram import Bot
from yookassa import Configuration, Payment
import logging
from nats.aio.msg import Msg

from services.services import save_excel
from database.database import get_order_in_db, get_payment_in_db, save_payment_in_db, update_order_in_db

logger = logging.getLogger('bot_app.'+__name__)

PAYMENT_ID_SPLIT = str(os.getenv('PAYMENT_ID')).split(';')
Configuration.configure(account_id=PAYMENT_ID_SPLIT[0], secret_key=PAYMENT_ID_SPLIT[1])





async def get_payment(payload: dict,
                         value: Decimal=10000.00,
                         return_url=os.getenv('RETURN_URL'),
                         description='Нет описания',
                         email='admin@gmail.com',
                         inn=os.getenv('INN')):
    
    payment = Payment.create({
        "amount": {
            "value": value,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "receipt": {
            "customer": {
                "full_name": "BOT_BOT",
                "inn": inn,
                "email": email,
            },

            "items": [
                        {
                            "description": description,
                            "quantity": "1",
                            "vat_code": "1",
                            "amount": {
                                "value": value,
                                "currency": "RUB"
                            },
                        }
                    ]
        },
        "capture": True,
        "metadata": payload,
        "description": description
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url, payment.id

async def check_payment_true(bot: Bot, payment: Payment, msg: Msg|None = None):

    if msg:
        pay_id = payment['object']['id']
        amount = Decimal(payment['object']['amount']['value'])
        amount_net = Decimal(payment['object']['income_amount']['value'])
        metadata = payment['object']['metadata']

        order_id = int(metadata['order_id'])
        user_id = int(metadata['user_id'])
        message_id = int(metadata['message_id'])
    else:
        pay_id = payment.id
        amount = Decimal(payment.amount.value)
        amount_net = Decimal(payment.income_amount.value)
        metadata = payment.metadata
        order_id = int(metadata.get('order_id'))
        user_id = int(metadata.get('user_id'))
        message_id = int(metadata.get('message_id'))
        

    try: 
        await bot.delete_message(chat_id=user_id, message_id=message_id)
        logger.debug(f"Удалил сообщение user_id ({user_id}) message_id ({message_id})")
    except Exception as e:
        logger.warning(f"Error delete_message user_id ({user_id}): {e}")

    info = await get_payment_in_db(pay_id)
    if info:
        if msg:
            await msg.ack()
        else:
            await bot.send_message(chat_id=user_id, text='Платёж уже зачислен')
        return
    else:
        await save_payment_in_db(pay_id, amount, amount_net, user_id, order_id)
        await update_order_in_db(order_id)

        # Отправить куда то заказ
        info = await get_order_in_db(order_id)
        order_data = info['order_data']
        address = info['address']
        total_price = info['total_price']

        await bot.send_message(chat_id=user_id, text=f'Заказ №{order_id} успешно оплачен. Ожидайте доставку.')

        await save_excel(user_id, order_id, order_data, address, total_price)

        if msg:
            await msg.ack()

