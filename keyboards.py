from aiogram import types

def get_main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Добавить книгу", callback_data="add_book"))
    keyboard.add(types.InlineKeyboardButton(text="Просмотр списка всех книг", callback_data="list_book"))
    keyboard.add(types.InlineKeyboardButton(text="Поиск книги", callback_data="search_book"))
    return keyboard

def back_to_menu():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="В меню", callback_data="menu"))
    return keyboard

def choose_book_for_delete():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Удалить книгу", callback_data=f"get_id_book"))
    return keyboard


def book_number_keyboard(book_id):
    # Создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="К списку", callback_data="list_book"))
    keyboard.add(types.InlineKeyboardButton(text="Удалить книгу", callback_data=f"delete_book_{book_id}"))
    keyboard.add(types.InlineKeyboardButton(text="В меню", callback_data="menu"))
    return keyboard

def list_book_keyboard():
    # Создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Поиск по жанру", callback_data="list_genre"))
    keyboard.add(types.InlineKeyboardButton(text="В меню", callback_data="menu"))
    return keyboard

def search_book_keyboard():
    # Создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Поиск по ключевому слову", callback_data="search_key_word"))
    keyboard.add(types.InlineKeyboardButton(text="Поиск по названию и/или автору", callback_data="search_name_author"))
    return keyboard
