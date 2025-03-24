import logging
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from decimal import Decimal
from config.config import FAQ_DATA
from database.database import get_all_products, get_cart, get_categories, get_product, get_products, get_sub_categories

logger = logging.getLogger('bot_app.'+__name__)


async def shop_main_menu_getter(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.dialog_data.get('user_id') or int(dialog_manager.start_data['user_id'])
    logger.debug(f'Getting main menu for user_id: {user_id}')
    dialog_manager.dialog_data['user_id'] = user_id
    info = await get_cart(user_id=user_id)
    is_cart = True if info else False
        
    return {'is_cart': is_cart}

async def shop_categories_getter(dialog_manager: DialogManager, **kwargs):
    info = await get_categories()
    sorted_categories = sorted((i['name'], i['id']) for i in info)
    
    # Пагинация
    items_per_page = 9
    total_items = len(sorted_categories)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    current_page = dialog_manager.dialog_data.get('current_page', 1)
    if current_page > total_pages:
        current_page = 1
        dialog_manager.dialog_data['current_page'] = 1
    
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    current_categories = sorted_categories[start_idx:end_idx]
    is_pagination = total_pages > 1
    
    dialog_manager.dialog_data['total_pages'] = total_pages
    
    return {
        'categories': current_categories,
        'is_pagination': is_pagination,
        'current_page': current_page,
        'total_pages': total_pages
    }


async def shop_sub_categories_getter(dialog_manager: DialogManager, **kwargs):
    info = await get_sub_categories(int(dialog_manager.dialog_data['id_category']))
    if info:
        sorted_sub_categories = sorted((i['name'], i['id']) for i in info)
        
        # Пагинация
        items_per_page = 9
        total_items = len(sorted_sub_categories)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        current_page = dialog_manager.dialog_data.get('current_page_sub', 1)
        if current_page > total_pages:
            current_page = 1
            dialog_manager.dialog_data['current_page_sub'] = 1
        
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        current_sub_categories = sorted_sub_categories[start_idx:end_idx]
        is_pagination = total_pages > 1
        
        dialog_manager.dialog_data['total_pages_sub'] = total_pages
        
        return {
            'sub_categories': current_sub_categories,
            'is_pagination': is_pagination,
            'current_page': current_page,
            'total_pages': total_pages
        }
    else:
        return {'sub_categories': [], 'is_pagination': False}


async def shop_products_getter(dialog_manager: DialogManager, **kwargs):
    info = await get_products(int(dialog_manager.dialog_data['id_sub_category']))
    if info:
        sorted_products = sorted((i['name'], i['id']) for i in info)
        
        # Пагинация
        items_per_page = 9
        total_items = len(sorted_products)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        current_page = dialog_manager.dialog_data.get('current_page_prod', 1)
        if current_page > total_pages:
            current_page = 1
            dialog_manager.dialog_data['current_page_prod'] = 1
        
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        current_products = sorted_products[start_idx:end_idx]
        is_pagination = total_pages > 1
        
        dialog_manager.dialog_data['total_pages_prod'] = total_pages
        
        return {
            'products': current_products,
            'is_pagination': is_pagination,
            'current_page': current_page,
            'total_pages': total_pages
        }
    else:
        return {'products': [], 'is_pagination': False}
    

async def shop_product_info_getter(dialog_manager: DialogManager, **kwargs):
    name_product = dialog_manager.dialog_data['name_product']
    counts = [(i, i) for i in range(1, 10)]
    return {'name_product': name_product, 'counts': counts}


async def shop_cart_getter(dialog_manager: DialogManager, **kwargs):
    async def grouped_poducts(list_products: list[dict]) -> list[dict]:
        grouped_products = {}
        for product in list_products:
            product_id = product['product_id']
            count = product['count']
            id_cart = product['id']
            user_id = product['user_id']


            if product_id in grouped_products:
                grouped_products[product_id]['count'] += count
            else:
                grouped_products[product_id] = {
                    'id': id_cart,
                    'product_id': product_id,
                    'count': count,
                    'user_id': user_id
                }

        return list(grouped_products.values())
    

    user_id = int(dialog_manager.dialog_data['user_id'])
    info = await get_cart(user_id=user_id)
    if info:
        all_products = await get_all_products()
        product_list = []
        new_info = await grouped_poducts(info)
        total_price: Decimal = 0
        order = []
        for product in new_info:
            id_cart = product['id']
            count = product['count']
            product_id = product['product_id']
            product_name = all_products[product_id]['name']
            product_price = Decimal(all_products[product_id]['price'])
            product_total = int(count) * product_price
            product_list.append(f'{product_name} - {count} шт. - {product_total} руб.')
            total_price += product_total

            order.append({'id_product': id_cart, 'product_name': product_name, 'amount': count})

        products = '=' * 30 + '\n'
        products += f'\n{"-"*40}\n'.join([product for product in product_list])
        products += '\n'+ '=' * 30

        address = dialog_manager.dialog_data.get('address')
        if address:
            is_address = True
        else:
            is_address = False

        dialog_manager.dialog_data['order'] = order
        dialog_manager.dialog_data['total_price'] = str(total_price)


        return {'products': products, 'is_cart': True, 'total_price': total_price,
                 'address': address, 'is_address': is_address}
    else:
        return {'products': 'Корзина пуста', 'is_cart': False, 'total_price': 0, 'is_address': False}
    

async def shop_faq_getter(dialog_manager: DialogManager, **kwargs):
    faq_data = FAQ_DATA
    search_query = dialog_manager.dialog_data.get('search_query', '').lower()
    
    if search_query:
        filtered_questions = [
            (question, answer) for question, answer in faq_data
            if search_query in question.lower()
        ]
        is_search = True
    else:
        filtered_questions = faq_data
        is_search = False

    # Пагинация
    items_per_page = 4 # количество вопросов на странице
    total_items = len(filtered_questions)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    dialog_manager.dialog_data['total_pages_faq'] = total_pages
    
    current_page = dialog_manager.dialog_data.get('current_page_faq', 1)
    logger.info(f'current_page_faq: {current_page}')
    logger.info(f'total_pages_faq: {total_pages}')
    if current_page > total_pages:
        current_page = 1
        dialog_manager.dialog_data['current_page_faq'] = 1
    
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    current_questions = filtered_questions[start_idx:end_idx]
    is_pagination = total_pages > 1

    # Убедимся, что item_id — короткая строка
    questions = [(q, str(i)) for i, (q, _) in enumerate(current_questions)]
    
    dialog_manager.dialog_data['faq_answers'] = dict(faq_data)

    
    return {
        'questions': questions,
        'search_query': search_query or 'Выберите вопрос или начните вводить для поиска',
        'is_search': is_search,
        'is_pagination': is_pagination,
        'current_page_faq': current_page,
        'total_pages_faq': total_pages
    }

async def shop_faq_answer_getter(dialog_manager: DialogManager, **kwargs):
    question = dialog_manager.dialog_data.get('selected_question', '')
    answer = dialog_manager.dialog_data.get('faq_answers', {}).get(question, 'Ответ не найден')
    
    return {
        'question': question,
        'answer': answer
    }

