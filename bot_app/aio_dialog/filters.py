import logging


logger = logging.getLogger('bot_app.'+__name__)

def count_input_check(text: str) -> int:
    try:
        count = int(text)
        if count > 0:
            return count
        raise ValueError
    except Exception as e:
        raise ValueError

def address_input_check(text: str) -> str:
    if text:
        return text
    raise ValueError

def text_input_check(text: str) -> str:
    if text:
        return text
    raise ValueError