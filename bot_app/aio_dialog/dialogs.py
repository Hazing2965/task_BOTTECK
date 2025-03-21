from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Cancel, Start, Group, Select, Button, Url, Back, Row
from aiogram_dialog.widgets.text import Const, Multi, Format

from aio_dialog.states import FaqState, ShopState
from aio_dialog.getters import (
    shop_cart_getter, shop_categories_getter, shop_main_menu_getter,
    shop_product_info_getter, shop_products_getter, shop_sub_categories_getter,
    shop_faq_getter, shop_faq_answer_getter
)
from aio_dialog.buttons import (
    category_select, clear_cart, count_select, create_payment, open_catlog_button,
    product_select, sub_categories_select, prev_page_categories, next_page_categories,
    prev_page_sub_categories, next_page_sub_categories, prev_page_products, next_page_products,
    select_faq_question, back_to_faq
)
from aio_dialog.services import address_input_correct, count_input_correct, count_input_uncorrect, no_text, search_faq
from aio_dialog.filters import address_input_check, count_input_check, text_input_check

shop_dialog = Dialog(
    Window(
        Multi(
            Const('Добро пожаловать в магазин!'),
            sep='\n\n'
        ),

        Button(Const('Каталог 🛍️'), id='open_catalog', on_click=open_catlog_button),
        SwitchTo(Const('Корзина 🛒'), id='open_cart', state=ShopState.cart, when=F['is_cart']),
        getter=shop_main_menu_getter,
        state=ShopState.main_menu,
    ),
    Window(
        Multi(
            Const('Корзина 🛒'),
            Format('{products}'),
            Format('Адрес доставки: {address}', when=F['is_address']),
            Format('Сумма заказа: <b>{total_price} руб.</b>'),
            sep='\n\n'
        ),
        Group(
            Button(Const('Оформить заказ'), id='order_products', on_click=create_payment, when=F['is_address']),

            SwitchTo(Const('Изменить адрес доставки'), id='change_address', state=ShopState.add_address, when=F['is_address']),
            SwitchTo(Const('Указать адрес доставки'), id='change_address', state=ShopState.add_address, when=~F['is_address']),

            Button(Const('Очистить корзину'), id='clear_cart', on_click=clear_cart),
            when=F['is_cart']
        ),
        SwitchTo(Const('Вернуться'), id='back_to_main_menu', state=ShopState.main_menu),
        getter=shop_cart_getter,
        state=ShopState.cart,
    ),
    Window(
        Multi(
            Const('Оформление заказа 🛒'),
            Const('Укажите адрес доставки'),
            sep='\n\n'
        ),
        TextInput(id='address_input',
                  type_factory=address_input_check,
                  on_success=address_input_correct),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        SwitchTo(Const('Отмена'), id='back_to_cart', state=ShopState.cart),
        state=ShopState.add_address,
    ),
    Window(
        Multi(
            Const('Каталог 🛍️'),
            Const('Выберите категорию'),
            sep='\n\n'
        ),
        Group(Select(
            Format('{item[0]}'),
            id='category',
            item_id_getter=lambda x: x[1],
            items='categories',
            on_click=category_select,
        ),
        width=3),
        Row(
            Button(Const('<<'), id='prev_page', on_click=prev_page_categories),
            Button(Format('{current_page}/{total_pages}'), id='page_number'),
            Button(Const('>>'), id='next_page', on_click=next_page_categories),
            when=F['is_pagination']
        ),
        SwitchTo(Const('Вернуться'), id='back_to_main_menu', state=ShopState.main_menu),
        state=ShopState.categories,
        getter=shop_categories_getter,
    ),
    Window(
        Multi(
            Const('Каталог 🛍️'),
            Const('Выберите подкатегорию', when=F['sub_categories']),
            Const('В данной категории нет подкатегорий', when=~F['sub_categories']),
            sep='\n\n'
        ),
        Group(Select(
            Format('{item[0]}'),
            id='sub_category',
            item_id_getter=lambda x: x[1],
            items='sub_categories',
            on_click=sub_categories_select,
        ),
        width=3, when=F['sub_categories']),
        Row(
            Button(Const('<<'), id='prev_page', on_click=prev_page_sub_categories),
            Button(Format('{current_page}/{total_pages}'), id='page_number'),
            Button(Const('>>'), id='next_page', on_click=next_page_sub_categories),
            when=F['is_pagination']
        ),
        SwitchTo(Const('Вернуться'), id='back_to_categories', state=ShopState.categories),
        state=ShopState.sub_categories,
        getter=shop_sub_categories_getter,
    ),
    Window(
        Multi(
            Const('Каталог 🛍️'),
            Const('Выберите продукт', when=F['products']),
            Const('В данной подкатегории нет продуктов', when=~F['products']),
            sep='\n\n'
        ),
        Group(Select(
            Format('{item[0]}'),
            id='product',
            item_id_getter=lambda x: x[1],
            items='products',
            on_click=product_select,
        ),
        width=3, when=F['products']),
        Row(
            Button(Const('<<'), id='prev_page', on_click=prev_page_products),
            Button(Format('{current_page}/{total_pages}'), id='page_number'),
            Button(Const('>>'), id='next_page', on_click=next_page_products),
            when=F['is_pagination']
        ),
        SwitchTo(Const('Вернуться'), id='back_to_sub_categories', state=ShopState.sub_categories),
        state=ShopState.products,
        getter=shop_products_getter,
    ),
    Window(
        Multi(
            Const('Добавление в корзину 🛒'),
            Format('Продукт: <b>{name_product}</b>'),
            sep='\n\n'
        ),
        SwitchTo(Const('Добавить в корзину'), id='add_to_cart', state=ShopState.count_add),
        SwitchTo(Const('Вернуться'), id='back_to_products', state=ShopState.products),
        getter=shop_product_info_getter,
        state=ShopState.product_info,
    ),
    Window(
        Multi(
            Const('Добавление в корзину 🛒'),
            Format('Продукт: <b>{name_product}</b>'),
            Const('Укажите количество (Выбрите или напишите число)'),
            # Format('Количество: {count_add}'),
            sep='\n\n'
        ),
        Group(Select(
            Format('{item[0]}'),
            id='count',
            item_id_getter=lambda x: x[1],
            items='counts',
            on_click=count_select,
            ),
            width=3),
        TextInput(id='count_input',
                  type_factory=count_input_check,
                  on_success=count_input_correct,
                  on_error=count_input_uncorrect),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        SwitchTo(Const('Отмена'), id='back_to_products', state=ShopState.products),
        getter=shop_product_info_getter,
        state=ShopState.count_add,
    )
)

faq_dialog = Dialog(
    Window(
        Multi(
            Const("❓ Часто задаваемые вопросы"),
            Format("\n🔍 Поиск: {search_query}"),
            sep="\n\n"
        ),
        TextInput(
            id="search",
            type_factory=text_input_check,
            on_success=search_faq
        ),
        Group(
            Select(
                Format("📝 {item[0]}"),
                id="question",
                item_id_getter=lambda x: x[0],
                items="questions",
                on_click=select_faq_question
            ),
            width=1
        ),
        
        state=FaqState.faq,
        getter=shop_faq_getter
    ),
    Window(
        Multi(
            Const("❓ Часто задаваемые вопросы"),
            Format("\n\n📝 Вопрос:\n{question}"),
            Format("\n\n📄 Ответ:\n{answer}"),
            sep=""
        ),
        Button(Const("🔙 К списку вопросов"), id="back_to_list", on_click=back_to_faq),
        
        state=FaqState.faq_answer,
        getter=shop_faq_answer_getter
    )
)