from app import db
from app.models import User, Tag, Review, Author, Book


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