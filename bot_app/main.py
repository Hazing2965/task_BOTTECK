import asyncio
import logging
import os


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs

from aio_dialog.dialogs import shop_dialog, faq_dialog

from services.nats_services import NATSClient, distribut_message, payment_message
from services.main_menu import set_main_menu
from hanlders import callback_handlers, other_handlers
from services.middlewars import UserSend
from hanlders import default_handlers, error_handlers
from config.config import setup_logger
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder

logger = logging.getLogger('bot_app.' + __name__)


async def main():
    await setup_logger()
    logger.info('Starting bot')

    redis = Redis(host=os.getenv('REDIS_HOST'))

    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    bot: Bot = Bot(token=os.getenv('BOT_TOKEN'),
                   default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher(storage=storage)

    setup_dialogs(dp)
    
    dp.update.middleware(UserSend())


    dp.include_router(callback_handlers.router)
    dp.include_router(default_handlers.router)

    dp.include_router(shop_dialog)
    dp.include_router(faq_dialog)

    dp.include_router(other_handlers.router)
    dp.include_router(error_handlers.router)



    nats_client = NATSClient()
    await nats_client.connect()
    await nats_client.create_stream()
    await nats_client.disconnect()

    asyncio.create_task(NATSClient().start_consumer(subject=os.getenv('SUBJECT_DISTRIBUT'), 
                                                   cb_funk=distribut_message, 
                                                   durable_name='distribut_message',
                                                   payload={'bot': bot}))
    
    asyncio.create_task(NATSClient().start_consumer(subject=os.getenv('SUBJECT_PAYMENT'), 
                                                   cb_funk=payment_message, 
                                                   durable_name='payment_message',
                                                   payload={'bot': bot}))

    
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, )


if __name__ == "__main__":
    asyncio.run(main())