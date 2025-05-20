"""В этом файле будут находиться все обработчики маршрутов на сайте"""

from flask import render_template, redirect, url_for, flash, request

from app import app, services

from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import RegisterForm, LoginForm, AddBookForm
from app.models import User, Book
from app.services import get_reviews_for_book, get_user_reviews, get_review_detail, get_all_tags, add_tag_for_book, \
    get_all_books, get_last_books


@app.route("/")
@app.route("/index")
def index():
    """
    Параметр local_css_file нужен для подключения css файла конкретной страницы
    Это сделано для того, что бы не пришлось писать один огромный css файл
    И что бы пользователям не надо было грузить большое кол-во ненужных css свойств для каждой страницы
    """

    params = {"title": "Главная",
              "books": get_last_books(),
              "local_css_file": "index.css"}

    return render_template("index.html", **params)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        # Проверка данных
        user = User.is_exists(form.username.data)
        if not user:
            flash("Такого пользователя не существует")
            return redirect(url_for("login"))

        if not user.check_password(form.password.data):
            flash("Введён неверный пароль")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)

        # Если не авторизованный юзер был перекинут, то после логина его вернёт на туже страницу
        return redirect(request.args.get("next") or url_for("users", value=current_user.username))

    params = {"title": "Авторизация",
              "local_css_file": "authorization.css",
              "form": form}

    return render_template("login.html", **params)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Проверка на уникальность email и username
        is_exists = User.is_exists(form.username.data, form.email.data)
        if is_exists:
            return "Пользователь с таким Username или Email уже существует", 404

        # Начинаем создавать пользователя
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        # Проверка специального кода для создания Админа
        if form.role.data == "admin":
            if form.admin_code.data != "ADMIN_CODE":
                return "Неверный Админ Код"
            else:
                user.role = "admin"

        # Добавляем пользователя в БД
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("index"))

    params = {"title": "Регистрация",
              "local_css_file": "authorization.css",
              "form": form}

    return render_template("register.html", **params)


@app.route("/users/<string:username>")
@login_required
def user_account(username):
    user = User.is_exists(username)

    if not user:
        return "Такого пользователя не существует"

    params = {"title": f"Профиль пользователя {username}",
              "local_css_file": "user_profile.css",
              "user": user}

    return render_template("user_profile.html", **params)


@app.route("/books")
def books_list():
    params = {"title": "Лента",
              "books": get_all_books(),
              "local_css_file": "book.css"}

    return render_template("books_ribbon.html", **params)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    params = {"local_css_file": "book.css"}

    book = Book.is_exists(book_id)
    if not book:
        return "Такой книги не сущесвутет", 404

    # Добавляем книгу в шаблон, если она существует
    params["book"] = book
    params["title"] = book.title

    return render_template("book_detail.html", **params)


# Добавление книги
@app.route("/books/add_book", methods=["GET", "POST"])
def add_book():
    # Форма добавления книги
    form = AddBookForm()
    # Задаём возможные теги
    available_tags = [tag.name for tag in get_all_tags()]
    form.tags.choices = [(tag, tag) for tag in available_tags]

    params = {"title": "Добавить книгу",
              "local_css_file": "book.css",
              "form": form,
              "available_tags": available_tags}

    if form.validate_on_submit():
        # Начинаем создавать книгу
        book = Book(title=form.title.data,
                    description=form.description.data)

        # Если указана ссылка на скачивание
        if form.link_to_download.data:
            book.link_to_download = form.link_to_download.data

        # Если добавлено фото
        if form.book_photo.data:
            book.set_photo(form.book_photo.data)

        # Получаем выбранные теги
        selected_tags = request.form.get("selected_tags", "").split(",")

        # Добавляем книгу в бд
        db.session.add(book)
        db.session.commit()

        # Добавляем выбранные теги в таблицу
        add_tag_for_book(book.id, selected_tags)

        # Перенаправляем на страницу с книгой
        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("create_book.html", **params)


# Все отзывы на конкретную книгу
@app.route("/books/<int:book_id>/reviews")
def book_reviews_list(book_id):
    params = {"title": "Отзывы",
              "local_css_file": "reviews.css"}

    # Берём все отзывы на книгу
    try:
        reviews = get_reviews_for_book(book_id)
        if reviews:
            params["reviews"] = reviews
    except Exception as e:
        params["error_message"] = str(e)

    return render_template("book_reviews.html", **params)


# Все отзывы конкретного пользователя
@app.route("/users/<string:username>/reviews")
def user_reviews(username):
    params = {"title": f"Отзывы",
              "local_css_file": "reviews.css"}

    # Берём все отзывы пользователя
    try:
        reviews = get_user_reviews(username)
        params["reviews"] = reviews
    except Exception as e:
        params["error_message"] = str(e)

    return render_template("user_reviews.html", **params)


# Детальзый отзыв
@app.route("/users/<string:username>/reviews/<int:review_id>")
def user_review_detail(username, review_id):
    params = {"title": "Отзывы",
              "local_css_file": "reviews.css"}

    # Получаем отзыв
    try:
        review = get_review_detail(username, review_id)
        params["review"] = review
    except Exception as e:
        params["error_message"] = str(e)

    return render_template("review_detail.html", **params)


@app.route("/authors")
def authors_list():
    return "Список всех авторов"


@app.route("/authors/<int:author_id>")
def author_detail(author_id):
    return "Все книги автора"
