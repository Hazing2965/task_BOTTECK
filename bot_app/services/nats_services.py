import asyncio
import json
import logging
import os

from pathlib import Path
from aiogram import Bot
from aiogram.types.input_file import FSInputFile
import nats
from nats.js.errors import BadRequestError
from nats.aio.msg import Msg
from nats.js.api import StreamConfig

from services.payment_services import check_payment_true
from database.database import det_info_distribut, update_distribut

logger = logging.getLogger('bot_app.' + __name__)

class NATSClient:
    def __init__(self, url: str=os.getenv('NATS_URL'), payload: dict = None):
        self.nc = None
        self.js = None
        self.cb_funk = None
        self.url = url
        self.payload = payload
        
    async def connect(self):
        self.nc = await nats.connect(self.url)
        self.js = self.nc.jetstream()

    async def disconnect(self):
        if self.nc:
            await self.nc.close()
            self.nc = None
            self.js = None
            self.cb_funk = None
            self.payload = None

    async def create_stream(self):
        if self.js is None:
            raise Exception("NATS не подключен")
        try:
            stream_config = StreamConfig(
                name=os.getenv('STREAM_NAME'),
                subjects=[
                    os.getenv('SUBJECT_DISTRIBUT'),
                    os.getenv('SUBJECT_PAYMENT')
                ],
                retention="limits",
                storage="file",  
                max_msgs=10000000,
                max_age=60 * 60 * 24 * 30, # 30 дней
                discard="old",
                allow_direct=True,  
            )
            try:
                await self.js.add_stream(stream_config)
            except BadRequestError as e:
                logger.warning("Это имя стрима уже занято и имеет другую конфигурацию")
                await self.js.delete_stream(os.getenv('STREAM_NAME'))
                await self.js.add_stream(stream_config)

        except Exception as e:
            logger.error(f"Error: {e}")



    async def on_message(self, msg: Msg):
        await self.cb_funk(msg, self.payload)

    async def start_consumer(self, cb_funk, subject: str, durable_name: str, payload: dict = None):
        await self.connect()
        
        if self.js is None:
            raise Exception("NATS не подключен")
        try:
            logger.info(f"Consumer started. Subject: {subject}")
            self.cb_funk = cb_funk
            self.payload = payload
            # Создаем push-консумера
            await self.js.subscribe(
                subject=subject,
                durable=durable_name,
                stream=os.getenv('STREAM_NAME'),
                cb=self.on_message,
                manual_ack=True,
            )


            while True:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error start_consumer: {e}\n\nsubject: {subject}")
        finally:
            await self.disconnect()

    
async def distribut_message(msg: Msg, payload: dict = None):
    bot: Bot = payload['bot']
    user_id = int(msg.data.decode('utf-8'))
    logger.info(f"distribut_message: {user_id}")
    id = int(msg.headers['id'])
    try:
        info = await det_info_distribut(id)
        if info:
            message = info.get('message')
            image = info.get('photo')
            image_id = info.get('photo_id')
            if image_id:
                await bot.send_photo(user_id, photo=image_id, caption=message, parse_mode='HTML')
            elif image:
                input_file = FSInputFile(path=f'media/{image}')
                message = await bot.send_photo(user_id, photo=input_file, caption=message, parse_mode='HTML')
                image_id = message.photo[-1].file_id
                await update_distribut(id, image_id)
            else:
                await bot.send_message(user_id, text=message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"user_id: {user_id}. Error distribut_message : {e}")
    await msg.ack()

async def payment_message(msg: Msg, payload: dict = None):
    message = msg.data.decode('utf-8')
    bot: Bot = payload['bot']
    
    try:
        data: dict = json.loads(message)
        await check_payment_true(bot, payment=data, msg=msg)
    except Exception as e:
        logger.error(f"Error payment_succeeded_consumer: {e}")


