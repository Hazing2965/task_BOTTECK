from aiogram.fsm.state import StatesGroup, State


class ShopState(StatesGroup):
    main_menu = State()
    
    categories = State()
    sub_categories = State()
    products = State()
    product_info = State()
    count_add = State()

    cart = State()
    add_address = State()

class FaqState(StatesGroup):

    faq = State()
    faq_answer = State()


