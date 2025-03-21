from datetime import datetime
from decimal import Decimal
import json
import os
import asyncpg
import logging
logger = logging.getLogger('bot_app.'+__name__)

async def connect_db():
    db = await asyncpg.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB'),
        host=os.getenv('POSTGRES_HOST')
    )
    return db

async def det_info_distribut(id: int):
    db = await connect_db()
    try:
        info = await db.fetchrow('SELECT * FROM myapp_distributionuser WHERE id = $1', id)
        if info:
            return dict(info)
        else:
            return None
    except Exception as e:
        raise Exception(f"Error det_info_distribut: {e}")

    finally:
        await db.close()

async def update_distribut(id: int, photo_id: str):
    db = await connect_db()
    try:
        await db.execute('UPDATE myapp_distributionuser SET photo_id = $1 WHERE id = $2', photo_id, id)
    except Exception as e:
        raise Exception(f"Error update_distribut: {e}")

    finally:
        await db.close()


async def new_user(id: int):
    db = await connect_db()
    try:
        if await db.fetchrow('SELECT * FROM myapp_usersbot WHERE user_id = $1', id):
            return
        await db.execute('INSERT INTO myapp_usersbot (user_id) VALUES ($1)', id)
    except Exception as e:
        raise Exception(f"Error new_user: {e}")
    finally:
        await db.close()


async def get_cart(user_id: int):
    db = await connect_db()
    try:
        info = await db.fetch('SELECT * FROM myapp_cart WHERE user_id = $1', user_id)
        if info:
            return [dict(row) for row in info]
        else:
            return None
    except Exception as e:
        raise Exception(f"Error get_cart: {e}")
    finally:
        await db.close()


async def get_products(id_sub_category = None):
    db = await connect_db()
    try:
        if id_sub_category is None:
            info = await db.fetch('SELECT * FROM myapp_product')

            return info
        else:
            info = await db.fetch('SELECT * FROM myapp_product WHERE sub_category_id = $1', id_sub_category)
        if info:
            return [dict(row) for row in info]
        else:
            return None
    except Exception as e:
        raise Exception(f"Error get_products: {e}")
    finally:
        await db.close()


async def get_categories():
    db = await connect_db()
    try:
        info = await db.fetch('SELECT * FROM myapp_categories')
        if info:
            return [dict(row) for row in info]
        else:
            return None
    except Exception as e:
        raise Exception(f"Error get_categories: {e}")
    finally:
        await db.close()


async def get_sub_categories(id_category: int):
    db = await connect_db()
    try:
        info = await db.fetch('SELECT * FROM myapp_subcategories WHERE category_id = $1', id_category)
        if info:
            return [dict(row) for row in info]
        else:
            return None
    except Exception as e:
        raise Exception(f"Error get_sub_categories: {e}")
    finally:
        await db.close()


async def get_product(id_product: int):
    db = await connect_db()
    try:
        info = await db.fetchrow('SELECT * FROM myapp_product WHERE id = $1', id_product)
        return dict(info)
    except Exception as e:
        raise Exception(f"Error get_product: {e}")
    finally:
        await db.close()

async def get_all_products():
    db = await connect_db()
    try:
        info = await db.fetch('SELECT * FROM myapp_product')
        if info:
            return {row['id']: dict(row) for row in info}  # Изменено для возврата словаря с id продукта как ключом
        else:
            return None
    except Exception as e:
        raise Exception(f"Error get_all_products: {e}")
    finally:
        await db.close()
    
async def insert_cart(user_id: int, id_product: int, count: int):
    db = await connect_db()
    try:
        await db.execute('INSERT INTO myapp_cart (user_id, product_id, count) VALUES ($1, $2, $3)', user_id, id_product, count)
    except Exception as e:
        raise Exception(f"Error insert_cart: {e}")
    finally:
        await db.close()


async def clear_cart_db(user_id: int):
    db = await connect_db()
    try:
        await db.execute('DELETE FROM myapp_cart WHERE user_id = $1', user_id)
    except Exception as e:
        raise Exception(f"Error clear_cart: {e}")
    finally:
        await db.close()


async def save_order(user_id: int, order: list, address: str, total_price: Decimal):
    db = await connect_db()
    try:
        order_id = await db.fetchval(
            'INSERT INTO myapp_orders (user_id, order_data, address, total_price, paid, date_create) '
            'VALUES ($1, $2, $3, $4, $5, $6) RETURNING id',
            user_id, json.dumps(order), address, total_price, False, datetime.now())
        return order_id
    except Exception as e:
        raise Exception(f"Error save_order: {e}")
    finally:
        await db.close()

async def get_order_in_db(order_id: int):
    db = await connect_db()
    try:
        info = await db.fetchrow('SELECT * FROM myapp_orders WHERE id = $1', order_id)
        return dict(info)
    except Exception as e:
        raise Exception(f"Error get_order_in_db: {e}")
    finally:
        await db.close()

async def update_order_in_db(order_id: int):
    db = await connect_db()
    try:
        await db.execute('UPDATE myapp_orders SET paid = TRUE, date_paid = $1 WHERE id = $2', datetime.now(), order_id)
    except Exception as e:
        raise Exception(f"Error update_order_in_db: {e}")
    finally:
        await db.close()

async def get_payment_in_db(pay_id: str):
    db = await connect_db()
    try:
        info = await db.fetchrow('SELECT * FROM myapp_payments WHERE payment_id = $1', pay_id)
        return info
    except Exception as e:
        raise Exception(f"Error get_payment_in_db: {e}")
    finally:
        await db.close()


async def save_payment_in_db(pay_id: str, amount: Decimal, amount_net: Decimal, user_id: int, order_id: int):
    db = await connect_db()
    try:
        await db.execute('INSERT INTO myapp_payments (payment_id, amount, amount_net, user_id, order_id) VALUES ($1, $2, $3, $4, $5)', pay_id, amount, amount_net, user_id, order_id)
    except Exception as e:
        raise Exception(f"Error save_payment_in_db: {e}")
    finally:
        await db.close()
