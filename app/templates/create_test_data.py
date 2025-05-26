"""
Внимание:::: Важная информация по запуску файла
В мейн ветке, откуда этот файл и будет вами скачан, файла базы данных - нет
Для того, что бы создался файл с настроенными таблицами вам нужно сделать 1 нетривиальное действие
а так же должно быть выполнено 1 условие
1) в проекте ДОЛЖНА лежать папка migrations СО ВСЕМИ её файлами, ни в коем случае её не меняйте!!!!
2) Откройте терминал, находясь в venv проекта, и напишите команду << flask db upgrade >> -
- Эта команда создаст вам пустой файл базы данных, но в которой будут все таблицы
3) Запускайте этот файл и тестовые данные будут добавлены!)
"""

from app import db, app
from app.models import User, Author, Book, Review, Tag, authors_books, books_tags, users_books
import os
import sqlalchemy as sa

# Функция для создания пользователей
def create_users():
    users = [
        {"username": "john_doe", "email": "john@example.com", "password": "password123"},
        {"username": "jane_smith", "email": "jane@example.com", "password": "password456"},
        {"username": "alice", "email": "alice@example.com", "password": "alicepass"},
        {"username": "bob", "email": "bob@example.com", "password": "bobpass"},
        {"username": "admin", "email": "admin@example.com", "password": "admin123", "role": "admin"}
    ]
    for user_data in users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data.get("role", "user")
        )
        user.set_password(user_data["password"])
        db.session.add(user)
    db.session.commit()

# Функция для создания авторов
def create_authors():
    authors = [
        {"name": "Лев", "surname": "Толстой", "patronymic": "Николаевич"},
        {"name": "Фёдор", "surname": "Достоевский", "patronymic": "Михайлович"},
        {"name": "Антон", "surname": "Чехов"},
        {"name": "Иван", "surname": "Бунин"},
        {"name": "Михаил", "surname": "Булгаков"}
    ]
    for author_data in authors:
        author = Author(
            name=author_data["name"],
            surname=author_data["surname"],
            patronymic=author_data.get("patronymic")
        )
        db.session.add(author)
    db.session.commit()

# Функция для создания тегов
def create_tags():
    tags = ["классика", "роман", "рассказ", "философия", "драма"]
    for tag_name in tags:
        tag = Tag(name=tag_name)
        db.session.add(tag)
    db.session.commit()

# Функция для создания книг
def create_books():
    books = [
        {
            "title": "Война и мир",
            "description": "Эпопея о войне и мире в России XIX века.",
            "authors": [{"name": "Лев Николаевич Толстой"}],
            "tags": ["классика", "роман"],
            "photo_path": "app/static/images/books_for_test_data/war_and_peace.jpg"
        },
        {
            "title": "Преступление и наказание",
            "description": "Роман о моральных и психологических переживаниях человека.",
            "authors": [{"name": "Фёдор Михайлович Достоевский"}],
            "tags": ["классика", "роман", "философия"],
            "photo_path": "app/static/images/books_for_test_data/crime_and_punishment.jpg"
        },
        {
            "title": "Мастер и Маргарита",
            "description": "Фантастический роман о любви и вере.",
            "authors": [{"name": "Михаил Афанасьевич Булгаков"}],
            "tags": ["классика", "роман", "философия"],
            "photo_path": "app/static/images/books_for_test_data/master_and_margarita.jpg"
        },
        {
            "title": "Человек в футляре",
            "description": "Рассказ о человеческой замкнутости и страхе перемен.",
            "authors": [{"name": "Антон Павлович Чехов"}],
            "tags": ["классика", "рассказ"],
            "photo_path": "app/static/images/books_for_test_data/man_in_a_case.jpg"
        },
        {
            "title": "Тёмные аллеи",
            "description": "Сборник рассказов о любви и судьбе.",
            "authors": [{"name": "Иван Александрович Бунин"}],
            "tags": ["классика", "рассказ"],
            "photo_path": "app/static/images/books_for_test_data/dark_alleys.jpg"
        }
    ]
    for book_data in books:
        book = Book(
            title=book_data["title"],
            description=book_data["description"],
            link_to_download=f"https://example.com/download/ {book_data['title'].replace(' ', '_')}"
        )
        # Добавляем фото
        if os.path.exists(book_data["photo_path"]):
            with open(book_data["photo_path"], "rb") as image_file:
                book.set_photo(image_file)
        db.session.add(book)
        db.session.commit()
        # Добавляем авторов
        add_authors_for_book(book.id, book_data["authors"])
        # Добавляем теги
        add_tag_for_book(book.id, book_data["tags"])

# Функция для добавления авторов для книги
def add_authors_for_book(book_id, authors):
    for author_dict in authors:
        author_row = author_dict["name"].split()
        author_surname = author_row[0]
        author_name = author_row[1]
        author_patronymic = author_row[2] if len(author_row) > 2 else None
        author = Author.is_exists(author_name, author_surname, author_patronymic)
        if not author:
            continue
        stmt = authors_books.insert().values(book_id=book_id, author_id=author.id)
        db.session.execute(stmt)
    db.session.commit()

# Функция для добавления тегов для книги
def add_tag_for_book(book_id, tags):
    for tag_name in tags:
        tag = Tag.is_exists(tag_name)
        if not tag:
            continue
        stmt = books_tags.insert().values(book_id=book_id, tag_id=tag.id)
        db.session.execute(stmt)
    db.session.commit()

# Функция для создания отзывов
def create_reviews():
    users = User.query.all()
    books = Book.query.all()
    for i in range(10):
        review = Review(
            title=f"Отзыв на книгу {i + 1}",
            text=f"Это текст отзыва номер {i + 1}. Книга очень интересная!",
            user_id=users[i % len(users)].id,
            book_id=books[i % len(books)].id
        )
        db.session.add(review)
    db.session.commit()

# Функция для назначения книг пользователям
def assign_books_to_users():
    users = User.query.all()
    books = Book.query.all()
    if not users or not books:
        print("Нет пользователей или книг для назначения.")
        return

    for user in users:
        # Назначаем каждому пользователю 3 случайные книги
        selected_books = books[:3]  # Первые 3 книги из списка
        for book in selected_books:
            stmt = sa.select(users_books).where(
                users_books.c.book_id == book.id,
                users_books.c.user_id == user.id
            )
            exists = db.session.execute(stmt).first()
            if not exists:
                insert_stmt = users_books.insert().values(book_id=book.id, user_id=user.id)
                db.session.execute(insert_stmt)
    db.session.commit()
    print("Книги успешно назначены пользователям.")

# Основная функция для заполнения базы данных
def populate_database():
    with app.app_context():  # Создаем контекст приложения
        print("Создание пользователей...")
        create_users()
        print("Создание авторов...")
        create_authors()
        print("Создание тегов...")
        create_tags()
        print("Создание книг...")
        create_books()
        print("Назначение книг пользователям...")
        assign_books_to_users()
        print("Создание отзывов...")
        create_reviews()
        print("База данных успешно заполнена!")

if __name__ == "__main__":
    populate_database()