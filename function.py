import sqlite3


# Завершение состояния
async def state_finish(state):
    try:
        await state.finish()
    except:
        pass

# Создание таблиц (если их нет)
def create_table():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY, name TEXT, author TEXT, description TEXT, genre TEXT)''')
    conn.commit()
    conn.close()

# Добавление книги в БД
async def add_book_to_db(data, genre_name):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (name, author, description, genre) VALUES (?, ?, ?, ?)",
                   (data['name'], data['author'], data['description'], genre_name))
    conn.commit()
    conn.close()

# Получение списка жанров
def get_genres():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Получаем уникальные жанры и их идентификаторы из таблицы книг
    cursor.execute("SELECT id, genre FROM books GROUP BY genre ORDER BY genre")

    genres = cursor.fetchall()
    conn.close()
    return genres

# Получение списка жанров по ID
def select_genres_from_id(genre_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT genre FROM books WHERE id = ?", (genre_id,))

    genre_row = cursor.fetchone()
    conn.close()

    if genre_row:
        return genre_row
    else:
        return None


# Вывод всех книг из БД
def get_all_books():
    conn = sqlite3.connect('library.db')  # Укажите путь к вашей базе данных
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, author, description, genre FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

# Уделение книги по ID
def delete_book_by_id(book_id):
    conn = sqlite3.connect('library.db')  # Замените 'your_database.db' на путь к вашей базе данных
    cursor = conn.cursor()

    # SQL-запрос на удаление книги по ID
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))

    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()

# Получение информации из БД по книге через ID
def get_book_by_id(book_id):
    conn = sqlite3.connect('library.db')  # Замените 'your_database.db' на путь к вашей базе данных
    cursor = conn.cursor()

    # SQL запрос для получения книги по ID
    cursor.execute("SELECT id, name, author, description, genre FROM books WHERE id = ?", (book_id,))

    # Получение одной записи
    book = cursor.fetchone()
    conn.close()

    return book


# Получение жанра определенной книги по ID
def get_genre_by_book_id(book_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute("SELECT genre FROM books WHERE id = ?", (book_id,))
    genre_row = cursor.fetchone()

    conn.close()

    if genre_row:
        return genre_row[0]
    else:
        return None


# Получение всех книг по определенному жанру
def get_books_by_genre(genre_name):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, author FROM books WHERE genre = ?", (genre_name,))
    books = cursor.fetchall()

    conn.close()

    return books


# Функция для поиска книг по ключевому слову
def search_books_by_keyword(key_word):
    # Подключение к вашей базе данных SQLite
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Поиск книг, где ключевое слово содержится в названии или авторе
    query = """SELECT id, name, author, description, genre 
               FROM books 
               WHERE name LIKE ? OR author LIKE ?"""
    cursor.execute(query, ('%' + key_word + '%', '%' + key_word + '%'))

    # Получение всех результатов
    books_found = cursor.fetchall()

    # Закрытие соединения с базой данных
    conn.close()

    return books_found


# Поиск книг по названию и\или автору
def search_books_in_db(search_query):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Разбиваем запрос на слова
    words = search_query.split()

    # Начинаем формировать запрос
    query = "SELECT * FROM books WHERE"

    # Добавляем условия поиска для каждого слова
    query_conditions = []
    for word in words:
        query_conditions.append(f"(name LIKE '%{word}%' OR author LIKE '%{word}%')")

    # Соединяем все условия через OR
    query += " OR ".join(query_conditions)

    cursor.execute(query)
    books = cursor.fetchall()
    conn.close()
    return books