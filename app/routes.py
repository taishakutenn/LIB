"""В этом файле будут находиться все обработчики маршрутов на сайте"""

from flask import render_template, redirect, url_for, flash, request

from app import app, services

from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import RegisterForm, LoginForm
from app.models import User
from app.services import get_reviews_for_book, get_user_reviews, get_review_detail


@app.route("/")
@app.route("/index")
def index():
    """
    Параметр local_css_file нужен для подключения css файла конкретной страницы
    Это сделано для того, что бы не пришлось писать один огромный css файл
    И что бы пользователям не надо было грузить большое кол-во ненужных css свойств для каждой страницы
    """

    params = {"title": "Главная",
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
              "local_css_file": "book.css"}

    return render_template("books_ribbon.html", **params)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    params = {"title": "Мор, ученик смерти",
              "local_css_file": "book.css"}

    return render_template("book_detail.html", **params)


@app.route("/add_book")
def add_book():
    return "Добавить книгу"


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
