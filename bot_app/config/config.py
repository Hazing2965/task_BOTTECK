import logging
from logging.handlers import RotatingFileHandler
import os

async def setup_logger():
    LOG_DIR = "/var/log/bot_app"
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger('bot_app')
    logger.setLevel(logging.DEBUG)

    logger.handlers.clear()

    log_format = logging.Formatter(
        "[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - \"{message}\"",
        style="{"
    )

    # Консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Файловый обработчик для DEBUG
    debug_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'debug.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(log_format)
    logger.addHandler(debug_handler)

    # Файловый обработчик для INFO
    info_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'info.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(log_format)
    logger.addHandler(info_handler)

    # Файловый обработчик для ERROR
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'error.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)


FAQ_DATA = [
        ("Как сделать заказ?", """
Чтобы сделать заказ:
1. Нажмите кнопку "Каталог 🛍️"
2. Выберите категорию товаров
3. Выберите подкатегорию
4. Выберите товар
5. Укажите количество
6. Перейдите в корзину
7. Укажите адрес доставки
8. Нажмите "Оформить заказ"
"""),
        ("Как оплатить?", """
Оплата заказа производится:
1. После оформления заказа
2. Через платежную систему
3. Банковской картой
4. Моментальное подтверждение
"""),
        ("Сроки доставки?", """
Сроки доставки зависят от вашего региона:
- Москва: 1-2 дня
- Санкт-Петербург: 2-3 дня
- Другие регионы: 3-7 дней
"""),
        ("Возврат товара", """
Условия возврата:
1. В течение 14 дней
2. Товар не был в использовании
3. Сохранен товарный вид
4. Имеется чек
"""),
        ("Где посмотреть статус?", """
Отследить статус заказа можно:
1. В личном кабинете
2. По номеру заказа
3. Через службу поддержки
"""),
        ("Есть ли скидки?", """
У нас действует система скидок:
1. Накопительная система баллов
2. Сезонные распродажи
3. Специальные предложения для постоянных клиентов
4. Акции в праздничные дни
5. Скидки на комплекты товаров
"""),
        ("Нужна помощь?", """
Способы связи с поддержкой:
1. Чат с оператором в боте
2. Email: support@example.com
3. Телефон: 8-800-XXX-XX-XX
4. Время работы: 24/7
"""),
        ("Что при повреждении ?", """
При получении поврежденного товара:
1. Сфотографируйте повреждения
2. Свяжитесь с поддержкой
3. Опишите проблему
4. Мы организуем возврат и замену
5. Все расходы берем на себя
"""),
    ]



