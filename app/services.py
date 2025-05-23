from dns.e164 import query

from app import db
from app.models import User, Tag, Review, Author, Book, books_tags, authors_books
import sqlalchemy as sa


# Функции для отзывов
def get_reviews_for_book(book_id):
    """Все отзывы для кокретной книги"""

    book = Book.is_exists(book_id)
    if not book:
        raise ValueError("Такой книги не существует")

    # Возвращаем все отзывы для книги
    return book.reviews


def get_user_reviews(username):
    """Все отзывы конкретного пользователя"""

    user = User.is_exists(username)
    if not user:
        raise ValueError("Такого пользователя не существует")

    # Возвращаем все отзывы пользователя
    return user.reviews


def get_review_detail(username, review_id):
    """Детальная страница отзыва"""

    # Проверяем на существование переданных значений
    is_user_exist = User.is_exists(username)
    if not is_user_exist:
        raise ValueError("Такого пользователя не сущесвует")

    is_review_exist = Review.is_exists(review_id)
    if not is_review_exist:
        raise ValueError("Отзыва с таким id не существует")

    return is_review_exist


def get_all_tags():
    """Возвращаем все теги на сервере"""

    return db.session.query(Tag).all()


def add_tag_for_book(book_id, tags):
    """Добавляет связи книга-тег в таблицу books_tags"""

    # Проверка на наличие тегов
    if not tags:
        return None

    # Проверка существования книги
    book = Book.is_exists(book_id)
    if not book:
        return None

    for tag_name in tags:
        tag = Tag.is_exists(tag_name)
        if not tag:
            continue  # Если тег не найден, пропускаем

        # Проверяем, нет ли уже такой связи
        stmt = sa.select(books_tags).where(
            books_tags.c.book_id == book_id,
            books_tags.c.tag_id == tag.id
        )
        exists = db.session.execute(stmt).first()

        if not exists:
            insert_stmt = books_tags.insert().values(book_id=book_id, tag_id=tag.id)
            db.session.execute(insert_stmt)

    db.session.commit()
    return True


def get_all_books():
    """Функция возвращающая все книги"""
    return db.session.query(Book).all()


def get_last_books():
    """Функция, возвращающая последние 9 добавленных книг на сайт"""
    return db.session.query(Book).limit(9)


def add_authors_for_book(book_id, authors):
    """Добавляет связи книга-автор в таблицу books_authora"""

    # Проверка на наличие авторов
    if not authors:
        return None

    # Проверка существования книги
    book = Book.is_exists(book_id)
    if not book:
        return None

    for author_dict in authors:
        # Преобразуем полученную строку в нужный для проверки автора вид
        author_row = author_dict["name"].split() # Сплитим по пробелу
        author_surname = author_row[0]
        author_name = author_row[1]
        if len(author_row) > 2:
            author_patronymic = author_row[2]
        else:
            author_patronymic = None

        author = Author.is_exists(author_name, author_surname, author_patronymic) # Проверяем существования автора
        if not author:
            # Если автор не найден - добавляем его в бд
            author = Author(name=author_name, surname=author_surname, patronymic=author_patronymic)
            db.session.add(author)
            db.session.commit()

        # Проверяем, нет ли уже такой связи
        stmt = sa.select(authors_books).where(
            authors_books.c.book_id == book_id,
            authors_books.c.author_id == author.id
        )
        exists = db.session.execute(stmt).first()

        if not exists:
            insert_stmt = authors_books.insert().values(book_id=book_id, author_id=author.id)
            db.session.execute(insert_stmt)

    db.session.commit()
    return True