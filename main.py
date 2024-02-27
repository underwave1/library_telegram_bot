from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Regexp
import logging
import sqlite3
from function import *
from config import *
from keyboards import *


# Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# Подключение к БД


# Вызов функции для созданиее БД и таблиц
create_table()

# определение состояний
class Form(StatesGroup):
    # состояния для создание книг
    waiting_for_name = State()
    waiting_for_author = State()
    waiting_for_description = State()

    # состояния для поиска книг
    waiting_for_search_key_word = State()
    waiting_for_search_name_author = State()

    waiting_for_genre_book = State()
    waiting_for_id_book = State()
    waiting_for_genre_search = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = get_main_menu_keyboard()
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Обработчик callback menu
@dp.callback_query_handler(lambda c: c.data == 'menu')
async def menu(callback_query: types.CallbackQuery):
    keyboard = get_main_menu_keyboard()
    # Отправка сообщения с клавиатурой основного меню
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,  # Добавляем message_id
        text='Выберите действие:',
        reply_markup=keyboard
    )



####################################
######### ДОБАВЛЕНИE КНИГИ #########
####################################


# Обработчик нажатия на кнопку "Добавить книгу"
@dp.callback_query_handler(text="add_book")
async def add_book_start(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await Form.waiting_for_name.set()
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,  # Добавляем message_id
        text='Введите название новой книги:',
    )

# Обработчик состояния waiting_for_name
@dp.message_handler(state=Form.waiting_for_name)
async def add_book_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    await message.answer("Введите автора книги:")

# Обработчик состояния waiting_for_author
@dp.message_handler(state=Form.waiting_for_author)
async def add_book_author(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['author'] = message.text
    await Form.next()
    await message.answer("Введите описание книги:")

# Обработчик состояния waiting_for_description
@dp.message_handler(state=Form.waiting_for_description)
async def add_book_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    genres = get_genres()  # Получаем список жанров и их ID из БД
    if genres:
        # Формируем список жанров для вывода пользователю, используя ID и название жанра
        genres_list = "\n".join([f"{genre[0]} - {genre[1]}" for genre in genres])
        reply_text = f"Выберите жанр, отправив номер, или отправьте свое название жанра:\n\n{genres_list}"
    else:
        reply_text = "Жанров еще не было добавлено, отправьте жанр:"

    await Form.waiting_for_genre_book.set()
    await message.answer(reply_text)


# Обработчик состояния waiting_for_genre_book
@dp.message_handler(state=Form.waiting_for_genre_book)
async def process_genre_book(message: types.Message, state: FSMContext):
    genre_input = message.text
    genre_name = None

    # Проверяем, является ли ввод числом
    if genre_input.isdigit():
        genre_id = int(genre_input)

        genre_row = select_genres_from_id(genre_id)

        if genre_row:
            genre_name = genre_row[0]
            async with state.proxy() as data:
                await add_book_to_db(data, genre_name)
                await state_finish(state)
                keyboard = back_to_menu()
                await message.answer("Книга успешно добавлена!", reply_markup=keyboard)
        else:
            keyboard = back_to_menu()
            await message.reply("Жанр с таким номером не найден. Попробуйте снова.", reply_markup=keyboard)
            return
    else:
        genre_name = genre_input
        async with state.proxy() as data:
            await add_book_to_db(data, genre_name)
            await state_finish(state)
            keyboard = back_to_menu()
            await message.answer("Книга успешно добавлена!", reply_markup=keyboard)




####################################
######### ПРОСМОТР КНИГ ############
####################################


# Обработчик callback list_book (вывод списка книг)
@dp.callback_query_handler(lambda c: c.data == 'list_book')
async def list_books(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    books = get_all_books()
    if books:
        reply_text = "Отправьте номер для управления книгой и получения подробностей:\n\n"
        for book in books:
            id, name, author, description, genre = book
            book_info = f"#{id}\nНазвание: {name}\nАвтор: {author}\n\n"
            reply_text += book_info

            keyboard = list_book_keyboard()
            await bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id,
                text=reply_text,
                reply_markup=keyboard
            )
    else:
        keyboard = back_to_menu()
        await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text='Библиотека пуста',
            reply_markup=keyboard
        )


# Обработчик, реагирующий на сообщения, состоящие только из цифр, для вывода информации о книге
@dp.message_handler(Regexp(r"^\d+$"))
async def book_details(message: types.Message):
    book_id = message.text  # ID книги будет текстом сообщения
    book = get_book_by_id(book_id)  # Функция для получения книги по ID из БД

    if book:
        id, name, author, description, genre = book
        book_info = f"Номер: {id}\n\nНазвание: {name}\n\nАвтор: {author}\n\nОписание: {description}\n\nЖанр: {genre}"

        keyboard = book_number_keyboard(book_id)

        await message.answer(book_info, reply_markup=keyboard)
    else:
        keyboard = back_to_menu()
        await message.answer("Книга с таким номером не найдена.", reply_markup=keyboard)


# Обработчик callback list_genre (вывод списка жанров)
@dp.callback_query_handler(lambda c: c.data == 'list_genre')
async def list_genre(callback_query: types.CallbackQuery):
    genres = get_genres()

    if genres:
        # Создание строки, где каждый жанр сопровождается его порядковым номером
        genres_text = "\n".join([f"{genre[0]} - {genre[1]}" for genre in genres])
    else:
        genres_text = "Жанры отсутствуют."

    keyboard = back_to_menu()

    # Отправляем сообщение с перечнем жанров
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=f"Выберите жанр (отправьте номер):\n\n{genres_text}",
        reply_markup=keyboard
    )

    await Form.waiting_for_genre_search.set()

# Обработчик состояния waiting_for_genre_search (поиск по жанрам)
@dp.message_handler(state=Form.waiting_for_genre_search)
async def process_genre_search(message: types.Message, state: FSMContext):
    book_id = message.text

    # Получаем жанр по ID книги
    genre_name = get_genre_by_book_id(book_id)

    if genre_name:
        # Получаем все книги данного жанра
        books = get_books_by_genre(genre_name)

        if books:
            books_list = "\n".join([f"#{book[0]}\nНазвание: {book[1]}\nАвтор: {book[2]}\n" for book in books])
            reply_text = f"Для подробного просмотра отправьте номер.\nКниги в жанре '{genre_name}':\n\n{books_list}"
        else:
            reply_text = f"Книг в жанре '{genre_name}' не найдено."
    else:
        reply_text = "Книга с таким ID не найдена или у неё нет жанра."

    keyboard = back_to_menu()
    await message.answer(reply_text, reply_markup=keyboard)
    await state_finish(state)  # Сброс состояния после обработки запроса



####################################
######### УДАЛЕНИЕ КНИГ ############
####################################



# Обработчик callback delete_book_ (удаление книги)
@dp.callback_query_handler(lambda c: c.data.startswith('delete_book_'))
async def delete_book(callback_query: types.CallbackQuery):
    # Извлекаем ID книги из callback_data
    book_id = callback_query.data.split('_')[2]  # получаем 'book_id' из 'delete_book_:book_id'

    delete_book_by_id(book_id)

    keyboard = back_to_menu()
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,  # Добавляем message_id
        text=f'Книга #{book_id} успешно удалена.',
        reply_markup=keyboard
    )


####################################
######### ПОИСК КНИГ ###############
####################################


# обработчик callback search_book (поиск книг)
@dp.callback_query_handler(lambda c: c.data == 'search_book')
async def search_book(callback_query: types.CallbackQuery):

    keyboard = search_book_keyboard()

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,  # Добавляем message_id
        text=f'Выберите вариант поиска:',
        reply_markup=keyboard
    )

# обработчик callback search_key_word (поиск книг по ключевому слову)
@dp.callback_query_handler(lambda c: c.data == 'search_key_word')
async def search_key_word(callback_query: types.CallbackQuery):


    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,  # Добавляем message_id
        text=f'Отправьте ключевое слово:',
    )


    await Form.waiting_for_search_key_word.set()


# обработчик состояния waiting_for_search_key_word (поиск книг по ключевому слову)
@dp.message_handler(state=Form.waiting_for_search_key_word)
async def process_genre_search(message: types.Message, state: FSMContext):
    key_word = message.text

    books_found = search_books_by_keyword(key_word)

    # Проверка, найдены ли книги
    if books_found:
        response = "Отправьте номер для получения подробной информации\n\nНайденные книги:\n" + "\n".join(
            [f"#{book[0]}: {book[1]}, Автор: {book[2]}" for book in books_found])
    else:
        response = "Книги по вашему запросу не найдены."

    keyboard = back_to_menu()
    await message.answer(response, reply_markup=keyboard)
    await state_finish(state)


# обработчик callback search_name_author (поиск книг по имени и\или автору)
@dp.callback_query_handler(lambda c: c.data == 'search_name_author')
async def search_name_author(callback_query: types.CallbackQuery):


    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,  # Добавляем message_id
        text=f'Введите название книги и\или автора\n\nПример(1):Импульс\nПример(2):Импульс + Ольга\nПример(3):Импульс + Ольга Сидорова',
    )


    await Form.waiting_for_search_name_author.set()


# обработчик состояния waiting_for_search_name_author (поиск книг по имени и\или автору)
@dp.message_handler(state=Form.waiting_for_search_name_author)
async def process_search_name_author(message: types.Message, state: FSMContext):
    search_query = message.text
    books = search_books_in_db(search_query)  # Функция поиска книг в базе данных
    if books:
        reply_text = "Найденные книги:\n\n"
        for book in books:
            id, name, author, description, genre = book
            book_info = f"#{id}\nНазвание: {name}\nАвтор: {author}\nЖанр: {genre}\n\n"
            reply_text += book_info
        keyboard = back_to_menu()
        await message.answer(reply_text,reply_markup=keyboard)
    else:
        keyboard = back_to_menu()
        await message.answer("Книги с таким названием или автором не найдены.", reply_markup=keyboard)
    await state_finish(state)



# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

