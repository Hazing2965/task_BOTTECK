from decimal import Decimal
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram.types.input_file import FSInputFile
import logging

from keyboards.callback_markup import create_payment_keyboard
from services.payment_services import get_payment
from hanlders.default_handlers import start_command
from database.database import clear_cart_db, get_product, get_products, insert_cart, save_order
from aio_dialog.states import FaqState, ShopState

logger = logging.getLogger('bot_app.'+__name__)

async def open_catlog_button(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    info = await get_products()
    if info:
        await dialog_manager.switch_to(state=ShopState.categories)
    else:
        await callback.message.answer('Каталог в данный момент пуст. Пожалуйста, загляните позже.')
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    
    

async def category_select(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, id_category: str):
    dialog_manager.dialog_data['id_category'] = id_category
    await dialog_manager.switch_to(state=ShopState.sub_categories)

async def sub_categories_select(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, id_sub_category: str):
    dialog_manager.dialog_data['id_sub_category'] = id_sub_category
    await dialog_manager.switch_to(state=ShopState.products)

async def product_select(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, id_product: str):
    info = await get_product(int(id_product))
    dialog_manager.dialog_data['id_product'] = id_product
    dialog_manager.dialog_data['name_product'] = info['name']
    dialog_manager.dialog_data['price_product'] = str(info['price'])
    text_list = []
    text_list.append(f'<b>{info["name"]}</b>')
    if info.get('description'):
        text_list.append(f'{info["description"]}')
    text_list.append(f'Цена: {info["price"]}')
    text = '\n\n'.join(text_list)

    if info.get('photo'):
        input_file = FSInputFile(path=f'media/{info.get("photo")}')
        await callback.bot.send_photo(callback.from_user.id, photo=input_file, caption=text, parse_mode='HTML')
    else:
        await callback.message.answer(text)
    
    await dialog_manager.switch_to(state=ShopState.product_info, show_mode=ShowMode.DELETE_AND_SEND)


async def clear_cart(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await clear_cart_db(callback.from_user.id)
    await callback.message.answer('Корзина очищена')
    await start_command(callback.message, dialog_manager)


async def create_payment(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    message = await callback.message.answer('Загрузка..')

    message_id = message.message_id
    order = dialog_manager.dialog_data['order']
    total_price = Decimal(dialog_manager.dialog_data['total_price'])
    address = dialog_manager.dialog_data['address']

    order_id = await save_order(user_id=callback.from_user.id, order=order, address=address, total_price=total_price)

    payment_url, payment_id = await get_payment(payload={'order_id': order_id, 'user_id': callback.from_user.id, 'message_id': message_id}, value=total_price, description=f'Заказ №{order_id}')

    # await callback.bot.delete_message(callback.from_user.id, message_id)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id, message_id=message_id, 
                                    text=f'Оплата заказа №{order_id}\nСумма: {total_price} руб.', 
                                    reply_markup=await create_payment_keyboard(payment_url, payment_id))


    await clear_cart_db(callback.from_user.id)
    await dialog_manager.done()

async def prev_page(callback: CallbackQuery, button: Button, manager: DialogManager):
    page_types = {
        'prev_page': 'current_page',
        'prev_page_sub': 'current_page_sub',
        'prev_page_prod': 'current_page_prod',
        'prev_page_faq': 'current_page_faq'
    }
    page_type = page_types.get(button.widget_id, 'current_page')
    current_page = manager.dialog_data.get(page_type, 1)
    logger.info(f'button.widget_id: {button.widget_id}')
    
    if current_page > 1:
        manager.dialog_data[page_type] = current_page - 1
    await callback.answer()

async def next_page(callback: CallbackQuery, button: Button, manager: DialogManager):
    page_types = {
        'next_page': ('current_page', 'total_pages'),
        'next_page_sub': ('current_page_sub', 'total_pages_sub'),
        'next_page_prod': ('current_page_prod', 'total_pages_prod'),
        'next_page_faq': ('current_page_faq', 'total_pages_faq')
    }
    
    current_key, total_key = page_types.get(button.widget_id)
    logger.info(f'current_key: {current_key} type: {type(current_key)}')
    logger.info(f'total_key: {total_key} type: {type(total_key)}')
    
    current_page = manager.dialog_data.get(current_key, 1)
    total_pages = manager.dialog_data.get(total_key, 1)

    logger.info(f'current_page: {current_page}')
    logger.info(f'total_pages: {total_pages}')
    if current_page < total_pages:
        manager.dialog_data[current_key] = current_page + 1
    await callback.answer()

async def count_select(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, value: str):
    id_product = dialog_manager.dialog_data['id_product']
    name_product = dialog_manager.dialog_data['name_product']
    user_id = callback.from_user.id
    logger.warning(f'value: {value}, user_id: {user_id}, id_product: {id_product}, name_product: {name_product}')
    await insert_cart(user_id=user_id, id_product=int(id_product), count=int(value))
    await callback.message.answer(text=f'🎉 Вы успешно добавили в корзину товар <b>{name_product}</b> в количестве <b>{value}</b> шт.! 🛒\n\n✨ Заказать можете в разделе <b>Корзина</b>.\n\n💫 Или добавьте ещё товары из нашего каталога, чтобы сделать вашу покупку ещё более увлекательной!')
    message = callback.message
    await start_command(message, dialog_manager)


async def select_faq_question(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, selected_question: str):
    dialog_manager.dialog_data['selected_question'] = selected_question
    await dialog_manager.switch_to(FaqState.faq_answer)
    await callback.answer()

async def back_to_faq(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.pop('search_query', None)
    await dialog_manager.switch_to(FaqState.faq)
    await callback.answer()

async def clear_search(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['search_query'] = ''
    await dialog_manager.switch_to(FaqState.faq)
    await callback.answer()