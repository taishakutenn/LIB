"""Это файл, в котором описаны модели базы данных"""

import io
from PIL import Image

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login

# Ассоциативная таблица для связи пользователей и книг (что они читали)
users_books = sa.Table(
    "users_books",
    db.metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("book_id", sa.Integer, sa.ForeignKey("books.id"), primary_key=True)
)


# Ассоциативная таблица для связи книг и тегов
books_tags = sa.Table(
    "books_tags",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("books.id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True)
)


# Ассоциативная таблица для связи книг и авторов
authors_books = sa.Table(
    "authors_books",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("books.id"), primary_key=True),
    sa.Column("author_id", sa.Integer, sa.ForeignKey("authors.id"), primary_key=True)
)


# Таблица Пользователей
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(50), index=True, unique=True, nullable=False)
    email = sa.Column(sa.String(120), index=True, unique=True, nullable=False)
    hashed_password = sa.Column(sa.String(256), nullable=True)
    status = sa.Column(sa.String(25), default="rejected", nullable=True)  # approved, pending
    role = sa.Column(sa.String(15), default="user", nullable=True)  # admin

    # Отношения к дочерним таблицам
    reviews = so.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    # Отношения многие ко многим
    books = so.relationship("Book", secondary=users_books, back_populates="users")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def avatar(self, size):
        """Этот метод генерирует URL-адрес пользователя на основе его почты.
        Если аватарки нет, Gravatar предоставляет случайный аватар."""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?s={size}&d=identicon"

    # Классметод для проверки существования пользователя
    @classmethod
    def is_exists(cls, username, email=None):
        return db.session.query(cls).filter((cls.username == username) | (cls.email == email)).first()


# Таблица Книг
class Book(db.Model):
    __tablename__ = "books"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(100), nullable=False, index=True)
    description = sa.Column(sa.String, nullable=True)
    link_to_download = sa.Column(sa.String, nullable=True)
    bin_preview_photo = sa.Column(sa.LargeBinary, nullable=True)

    # Отношения к дочерним таблицам
    reviews = so.relationship("Review", back_populates="book", cascade="all, delete-orphan")

    # Отношения многие ко многим
    tags = so.relationship("Tag", secondary=books_tags, back_populates="books")
    authors = so.relationship("Author", secondary=authors_books, back_populates="books")
    users = so.relationship("User", secondary=users_books, back_populates="books")

    def set_photo(self, file, max_size= 10 * 1024 * 1024):
        try:
            if not file or not hasattr(file, "read"):
                raise ValueError("Файл не задан или не является изображением")

            image_data = file.read()
            image_size = len(image_data)

            # Для адекватного распределения ресурсов
            if image_size > max_size:
                raise ValueError("Размер изображения слишком большой")

            # Что бы не повторилась история, как с 4chan)
            try:
                image = Image.open(io.BytesIO(image_data))
                image.verify()  # Проверяем, что это валидное изображение
            except Exception:
                raise ValueError("Файл не является изображением.")

            self.bin_preview_photo = image_data

        except IOError:
            raise ValueError(f"Ошибка при чтении файла {file}.")
        except Exception as e:
            raise ValueError(f"Произошла ошибка: {str(e)}")

    def get_photo(self):
        return self.bin_preview_photo

    # Классметод для проверки существования книги
    @classmethod
    def is_exists(cls, book_id):
        return db.session.query(cls).filter(cls.id == book_id).first()


# Таблица Авторов
class Author(db.Model):
    __tablename__ = "authors"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(50), nullable=False, index=True)
    surname = sa.Column(sa.String(50), nullable=False, index=True)
    patronymic = sa.Column(sa.String(75), nullable=True)

    # Отношения многие ко многим
    books = so.relationship("Book", secondary=authors_books, back_populates="authors")


# Таблица Тегов
class Tag(db.Model):
    __tablename__ = "tags"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(30), nullable=False, index=True)

    # Отношения многие ко многим
    books = so.relationship("Book", secondary=books_tags, back_populates="tags")


# Таблица Отзывов
class Review(db.Model):
    __tablename__ = "reviews"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(256), nullable=False)
    text = sa.Column(sa.String, nullable=False)

    # Поля для связи таблицы
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    book_id = sa.Column(sa.Integer, sa.ForeignKey("books.id"), nullable=False)

    # Отношения к родительским таблицам
    user = so.relationship("User", back_populates="reviews")
    book = so.relationship("Book", back_populates="reviews")

    # Классметод для проверки существования отзыва
    @classmethod
    def is_exists(cls, review_id):
        return db.session.query(cls).filter(cls.id == review_id).first()


# Функция для Flask-Login
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))