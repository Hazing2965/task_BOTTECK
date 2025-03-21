from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.input import ManagedTextInput
import logging

from aio_dialog.states import ShopState
from hanlders.default_handlers import start_command
from database.database import insert_cart

logger = logging.getLogger('bot_app.'+__name__)

async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.reply(text='Вы ввели вообще не текст')

async def count_input_correct(message: Message,
                             widget: ManagedTextInput,
                             dialog_manager: DialogManager,
                             value: int) -> None:
    
    id_product = dialog_manager.dialog_data['id_product']
    name_product = dialog_manager.dialog_data['name_product']
    await insert_cart(user_id=message.from_user.id, id_product=int(id_product), count=int(value))
    await message.answer(text=f'🎉 Вы успешно добавили в корзину товар <b>{name_product}</b> в количестве <b>{value}</b> шт.! 🛒\n\n✨ Заказать можете в разделе <b>Корзина</b>.\n\n💫 Или добавьте ещё товары из нашего каталога, чтобы сделать вашу покупку ещё более увлекательной!')
    await start_command(message, dialog_manager)


async def count_input_uncorrect(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.reply('Вы ввели не число или число меньше 0')


async def address_input_correct(message: Message,
                               widget: ManagedTextInput,
                               dialog_manager: DialogManager,
                               value: str) -> None:
    dialog_manager.dialog_data['address'] = value
    await dialog_manager.switch_to(ShopState.cart)


async def search_faq(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, query: str) -> None:
    dialog_manager.dialog_data['search_query'] = query
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND