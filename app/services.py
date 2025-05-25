import sqlalchemy as sa
from sqlalchemy import cast, desc, func, literal, String

from app import db
from app.models import (
    Author,
    Book,
    Review,
    Tag,
    User,
    authors_books,
    books_tags,
    users_books,
)


# --- Отзывы ---
def get_reviews_for_book(book_id):
    """Все отзывы для конкретной книги"""
    book = Book.is_exists(book_id)
    if not book:
        raise ValueError("Такой книги не существует")
    return book.reviews


def get_user_reviews(username):
    """Все отзывы конкретного пользователя"""
    user = User.is_exists(username)
    if not user:
        raise ValueError("Такого пользователя не существует")
    return user.reviews


def get_review_detail(username, review_id):
    """Детальная страница отзыва"""
    if not User.is_exists(username):
        raise ValueError("Такого пользователя не существует")
    review = Review.is_exists(review_id)
    if not review:
        raise ValueError("Отзыва с таким id не существует")
    return review


# --- Книги ---
def get_all_books(page):
    """Функция возвращающая все книги с определённой страницы"""
    count_books_in_page = 9
    return db.session.query(Book).limit(count_books_in_page).offset(page * count_books_in_page)


def get_detail_book(book_id):
    """Функция возвращающая конкретную книгу"""
    return db.session.query(Book).filter(Book.id == book_id).first()


def get_last_books():
    """Функция, возвращающая последние 9 добавленных книг на сайт"""
    return db.session.query(Book).order_by(Book.id.desc()).limit(9)


def add_book_for_user(book_id, user_id):
    try:
        stmt = sa.select(users_books).where(
            users_books.c.book_id == book_id,
            users_books.c.user_id == user_id
        )
        exists = db.session.execute(stmt).first()
        if not exists:
            insert_stmt = users_books.insert().values(book_id=book_id, user_id=user_id)
            db.session.execute(insert_stmt)
            db.session.commit()
            return True
        return None
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return False


def get_user_books(user_id):
    """Все книги пользователя"""
    user = db.session.get(User, user_id)  # Получаем пользователя по ID
    if not user:
        return []  # Если пользователь не найден, возвращаем пустой список
    return user.books  # Возвращаем список книг пользователя


# --- Авторы ---
def get_all_authors():
    """Функция возвращающая всех авторов"""
    return db.session.query(Author).all()


def add_authors_for_book(book_id, authors):
    """Добавляет связи книга-автор в таблицу authors_books"""
    if not authors:
        return None
    book = Book.is_exists(book_id)
    if not book:
        return None
    for author_dict in authors:
        author_row = author_dict["name"].split()
        author_surname = author_row[0]
        author_name = author_row[1]
        author_patronymic = author_row[2] if len(author_row) > 2 else None
        author = Author.is_exists(author_name, author_surname, author_patronymic)
        if not author:
            author = Author(name=author_name, surname=author_surname, patronymic=author_patronymic)
            db.session.add(author)
            db.session.commit()
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


# --- Теги ---
def get_all_tags():
    """Возвращаем все теги на сервере"""
    return db.session.query(Tag).all()


def add_tag_for_book(book_id, tags):
    """Добавляет связи книга-тег в таблицу books_tags"""
    if not tags:
        return None
    book = Book.is_exists(book_id)
    if not book:
        return None
    for tag_name in tags:
        tag = Tag.is_exists(tag_name)
        if not tag:
            continue
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


# --- Поиск ---
def search_ajax(search_word):
    """Регистрозависимый поиск по книгам, авторам и тегам"""
    result = {"books": [], "authors": [], "tags": []}

    books = db.session.query(Book).filter(
        func.lower(cast(Book.title, String)).like(f"%{search_word}%") |
        func.lower(cast(Book.description, String)).like(f"%{search_word}%")
    ).all()
    result["books"] = [
        {"id": book.id, "title": book.title, "description": book.description} for book in books
    ]

    full_name_expr = func.lower(
        cast(Author.surname, String) + literal(' ') +
        cast(Author.name, String) + literal(' ') +
        func.coalesce(cast(Author.patronymic, String), literal(''))
    )
    authors = db.session.query(Author).filter(
        full_name_expr.like(f"%{search_word}%")
    ).all()
    result["authors"] = [
        {
            "id": author.id,
            "full_name": f"{author.surname} {author.name} {author.patronymic or ''}".strip()
        } for author in authors
    ]

    tags = db.session.query(Tag).filter(
        func.lower(cast(Tag.name, String)).like(f"%{search_word}%")
    ).all()
    result["tags"] = [
        {"id": tag.id, "name": tag.name} for tag in tags
    ]

    return result


def get_books_for_search(page, search_word):
    """Функция возвращающая все книги с определённой страницы по поисковому слову"""
    count_books_in_page = 9  # Количество книг на странице

    # Создаем базовый запрос для книг
    query = db.session.query(Book)

    # Объединяем книги с авторами и тегами
    query = query.outerjoin(Book.authors).outerjoin(Book.tags)

    # Создаем объединенное выражение для ФИО авторов
    full_name_expr = (
        func.coalesce(Author.surname, '') + ' ' +
        func.coalesce(Author.name, '') + ' ' +
        func.coalesce(Author.patronymic, '')
    )

    # Удаляем лишние пробелы (если есть)
    full_name_expr = func.trim(full_name_expr)

    # Фильтруем по названию, описанию книги, ФИО авторов и тегам
    query = query.filter(
        (Book.title.like(f"%{search_word}%")) |
        (Book.description.like(f"%{search_word}%")) |
        (full_name_expr.like(f"%{search_word}%")) |  # Поиск по объединенному ФИО
        (Tag.name.like(f"%{search_word}%"))
    )

    # Подсчитываем общее количество найденных книг
    total_books = query.count()
    if total_books == 0:
        return []  # Возвращаем пустой список, если ничего не найдено

    # Применяем пагинацию
    books = query.limit(count_books_in_page).offset(page * count_books_in_page).all()

    return books
