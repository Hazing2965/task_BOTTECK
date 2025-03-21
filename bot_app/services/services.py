from datetime import datetime
import json
import logging
import os
import aiofiles
from openpyxl import Workbook, load_workbook

logger = logging.getLogger('bot_app.' + __name__)

async def save_excel(user_id, order_id, order_data, address, total_price):
    logger.info(f'save_excel: {user_id}, {order_id}, {order_data}, {address}, {total_price}')

    current_date = datetime.now().strftime('%d.%m.%Y %H:%M')
    file_name = f'{user_id}_{current_date}.xlsx'
    

    orders_dir = 'orders'
    file_path = os.path.join(orders_dir, file_name)
    
    if isinstance(order_data, str):
        order_data = json.loads(order_data)
    
    wb = Workbook()
    ws = wb.active
    

    headers = ['Номер заказа', 'Наименование продукта', 'ID в базе', 'Количество', 'Адрес', 'Сумма заказа']
    ws.append(headers)
    

    for i, item in enumerate(order_data):
        row_data = [
            order_id if i == 0 else '', 
            item['product_name'],
            item['id_product'],
            item['amount'],
            address if i == 0 else '',   
            total_price if i == 0 else '' 
        ]
        ws.append(row_data)
    

    os.makedirs(orders_dir, exist_ok=True)
    

    wb.save(file_path)
    
    