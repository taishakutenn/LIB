"""В этом файле будут находиться все обработчики маршрутов на сайте"""

from flask import render_template, redirect, url_for, flash, request
from app import app

from flask_login import current_user, login_user, logout_user, login_required
from is_safe_url import is_safe_url

from app import app, db
from app.forms import RegisterForm, LoginForm
from app.models import User


# @login_required


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

    next_page = request.args.get("next")

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
        next_page_post = request.form.get("next")
        print(next_page_post)

        if next_page_post and is_safe_url(next_page_post, ['127.0.0.1:5000']):
            return redirect(next_page_post)

        return redirect(url_for("index"))

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

    params = {"title": f"Профиль: {username}",
              "user": user}

    return render_template("user_profile.html", **params)
