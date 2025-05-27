"""В этом файле будут находиться все обработчики маршрутов на сайте"""

# Стандартные библиотеки
import flask
from flask import flash, jsonify, redirect, render_template, request, url_for

# Сторонние библиотеки
from flask_login import current_user, login_required, login_user, logout_user

# Локальные импорты
from app import app, db, services
from app.forms import AddBookForm, LoginForm, RegisterForm, CreateReviewForm, CreateAuthorForm
from app.models import Author, Book, User, Review
from app.services import (
    add_authors_for_book,
    add_book_for_user,
    add_tag_for_book,
    get_all_authors,
    get_all_books,
    get_all_tags,
    get_books_for_search,
    get_detail_book,
    get_last_books,
    get_review_detail,
    get_reviews_for_book,
    get_max_page,
    get_user_books,
    get_user_reviews,
    search_ajax,
)


# --- Главная страница ---
@app.route("/")
@app.route("/index")
def index():
    params = {"title": "Главная",
              "books": get_last_books(),
              "local_css_file": "index.css"}
    return render_template("index.html", **params)


# --- Страница о проекте ---
@app.route("/about_project")
@login_required
def about_project():
    params = {"title": "О проекте",
              "local_css_file": "index.css"}
    return render_template("for_project.html", **params)


# --- Аутентификация пользователей ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.is_exists(form.username.data)
        if not user:
            flash("Такого пользователя не существует")
            return redirect(url_for("login"))

        if not user.check_password(form.password.data):
            flash("Введён неверный пароль")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for("user_account", username=current_user.username))

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
        is_exists = User.is_exists(form.username.data, form.email.data)
        if is_exists:
            return "Пользователь с таким Username или Email уже существует", 404

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        if form.role.data == "admin":
            if form.admin_code.data != "ADMIN_CODE":
                return "Неверный Админ Код"
            else:
                user.role = "admin"

        db.session.add(user)
        db.session.commit()

        flash("Аккаунт успешно создан", "success")

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


# --- Работа с книгами ---
@app.route("/books")
def books_list():
    page = request.args.get("page")
    if not page:
        page = 0
    if int(page) < 0:
        return "Такой страницы не существует", 404

    params = {"title": "Лента",
              "books": get_all_books(int(page)),
              "max_page": get_max_page(), # Получаем максимальную страницу
              "current_page": int(page), # Для отображения текущей страницы
              "local_css_file": "book.css"}

    return render_template("books_ribbon.html", **params)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    params = {"local_css_file": "book.css"}
    book = Book.is_exists(book_id)
    if not book:
        return "Такой книги не сущесвутет", 404
    params["book"] = book
    params["title"] = book.title
    return render_template("book_detail.html", **params)


@app.route("/books/add_book", methods=["GET", "POST"])
def add_book():
    form = AddBookForm()
    available_tags = [tag.name for tag in get_all_tags()]
    form.tags.choices = [(tag, tag) for tag in available_tags]

    params = {"title": "Добавить книгу",
              "local_css_file": "book.css",
              "form": form,
              "available_tags": available_tags}

    if form.validate_on_submit():
        book = Book(title=form.title.data,
                    description=form.description.data)

        if not form.authors.data:
            return "Укажите хотя-бы одного автора", 404

        if form.link_to_download.data:
            book.link_to_download = form.link_to_download.data

        if form.book_photo.data:
            book.set_photo(form.book_photo.data)

        selected_tags = request.form.get("selected_tags", "").split(",")
        authors = form.authors.data

        db.session.add(book)
        db.session.commit()

        add_tag_for_book(book.id, selected_tags)
        result_add_authors = add_authors_for_book(book.id, authors)
        if not result_add_authors:
            return "Не удалось создать авторов", 404

        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("create_book.html", **params)


@app.route("/books/change_book/<int:book_id>", methods=["GET", "POST"])
def change_book(book_id):
    book = Book.is_exists(book_id)
    if not book:
        return "Такой книги не существует"

    form = AddBookForm(obj=book)
    available_tags = [tag.name for tag in get_all_tags()]
    form.tags.choices = [(tag, tag) for tag in available_tags]
    selected_tags = [tag.name for tag in book.tags]
    selected_authors = [" ".join([author.surname, author.name, author.patronymic if author.patronymic else ""]) for author in book.authors]

    params = {
        "title": "Изменить книгу",
        "local_css_file": "book.css",
        "form": form,
        "available_tags": available_tags,
        "selected_tags": selected_tags,
        "selected_authors": selected_authors
    }

    if form.validate_on_submit():
        change_flag = False
        if book.title != form.title.data:
            book.title = form.title.data
            change_flag = True
        if book.description != form.description.data:
            book.description = form.description.data
            change_flag = True
        if form.link_to_download.data and book.link_to_download != form.link_to_download.data:
            book.link_to_download = form.link_to_download.data
            change_flag = True
        if form.book_photo.data:
            book.set_photo(form.book_photo.data)
            change_flag = True

        new_selected_tags = request.form.get("selected_tags", "").split(",")
        current_tags = [tag.name for tag in book.tags]
        if sorted(new_selected_tags) != sorted(current_tags):
            book.tags = []
            db.session.commit()
            add_tag_for_book(book.id, new_selected_tags)
            change_flag = True

        authors = form.authors.data
        old_authors = [{"surname": a.surname, "name": a.name, "patronymic": a.patronymic} for a in book.authors]

        new_authors_data = []
        for author in authors:
            fio = author["name"].strip().split()
            if len(fio) == 3:
                new_authors_data.append({"surname": fio[0], "name": fio[1], "patronymic": fio[2]})

        if old_authors != new_authors_data:
            book.authors = []
            db.session.commit()
            result_add_authors = add_authors_for_book(book.id, authors)
            if not result_add_authors:
                return "Не удалось обновить авторов", 404
            change_flag = True

        if change_flag:
            db.session.commit()

        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("change_book.html", **params)


@app.route("/books/users/<string:username>")
def user_books(username):
    """Все книги пользователя"""

    # Проверяем, существует ли такой пользователь
    user = User.is_exists(username)
    if not user:
        return "Такого пользователя не существует", 404

    params = {"title": f"Книги пользователя: {username}",
              "books": get_user_books(user.id),
              "local_css_file": "book.css"}
    return render_template("user_books.html", **params)


@app.route("/books/delete_book/<int:book_id>")
@login_required
def delete_book(book_id):
    """Функция для удаления книги"""
    if current_user.role != "admin":  # Если пользователь не админ
        return "У вас нет прав на это", 403

    # Проверяем, существует ли такая книга
    book = Book.is_exists(book_id)
    if not book:
        return "Такой книги не существует", 404

    try:
        # Удаляем книгу из базы данных
        db.session.delete(book)
        db.session.commit()

        # Выводим сообщение об успешном удалении
        flask.flash("Книга успешно удалена", "success")

    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        db.session.rollback()
        flask.flash(f"Ошибка при удалении книги: {str(e)}", "error")
        return f"Ошибка при удалении книги: {str(e)}", 500

    # Перенаправляем пользователя на список книг
    return redirect(url_for("books_list"))


# --- Работа с отзывами ---
@app.route("/books/<int:book_id>/reviews")
def book_reviews_list(book_id):
    """Все отзывы на книгу"""
    params = {"title": "Отзывы",
              "book": get_detail_book(book_id),
              "local_css_file": "reviews.css"}
    try:
        reviews = get_reviews_for_book(book_id)
        if reviews:
            params["reviews"] = reviews
    except Exception as e:
        params["error_message"] = str(e)
    return render_template("book_reviews.html", **params)


@app.route("/users/<string:username>/reviews")
def user_reviews(username):
    """Все отзывы пользователя"""
    params = {"title": f"Отзывы",
              "user": User.is_exists(username),
              "local_css_file": "reviews.css"}
    try:
        reviews = get_user_reviews(username)
        params["reviews"] = reviews
    except Exception as e:
        params["error_message"] = str(e)
    return render_template("user_reviews.html", **params)


@app.route("/users/<string:username>/reviews/<int:review_id>")
def user_review_detail(username, review_id):
    """Детальная страница отзыва"""
    params = {"title": "Отзывы",
              "local_css_file": "reviews.css"}
    try:
        review = get_review_detail(username, review_id)
        params["review"] = review
    except Exception as e:
        params["error_message"] = str(e)
    return render_template("review_detail.html", **params)


@app.route("/users/<string:username>/reviews/create_review/<int:book_id>", methods=["GET", "POST"])
@login_required
def create_review(username, book_id):
    """Создание отзыва"""
    form = CreateReviewForm()
    params = {"title": "Создание отзыва",
              "form": form,
              "local_css_file": "book.css"}

    # Проверяем, сущесвутет ли юзер
    user = User.is_exists(username)
    if not user:
        return "Такого пользователя не существует", 404

    # Проверяем, существует ли книга
    book = Book.is_exists(book_id)
    if not book:
        return "Такой книги не существует", 404

    if form.validate_on_submit():
        # Создаём отзыв
        review = Review(title=form.title.data,
                        text=form.text.data,
                        user_id=user.id,
                        book_id=book.id)
        db.session.add(review)
        db.session.commit()

        return redirect(url_for("user_review_detail", username=user.username, review_id=review.id))

    return render_template("create_review.html", **params)


@app.route("/reviews/change_review/<int:review_id>", methods=["GET", "POST"])
@login_required
def change_review(review_id):
    "Изменение отзыва"

    # Проверяем, существует ли такой отзыв
    review = Review.is_exists(review_id)
    if not review:
        return "Такого отзыва не существует", 404

    # Проверяем, что админ или создатель отзыва
    if not current_user.role == "admin" and not current_user.id == review.user_id:
        return "У вас нет прав для этого", 403

    form = CreateReviewForm(obj=review)
    params = {"title": "Изменение отзыва",
              "form": form,
              "change": "yes", # Для проверки в шаблоне, что изменяем
              "local_css_file": "book.css"}

    if form.validate_on_submit():
        change_flag = False # Флаг изменения

        if form.title.data != review.title:
            review.title = form.title.data
            change_flag = True

        if form.text.data != review.text:
            review.text = form.text.data
            change_flag = True

        # Если были изменения
        if change_flag:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return f"Ошибка при сохранении изменений: {str(e)}", 500

        return redirect(url_for("user_review_detail", username=review.user.username, review_id=review.id))

    return render_template("create_review.html", **params)


@app.route("/reviews/delete_review/<int:review_id>")
@login_required
def delete_review(review_id):
    """Удаление отзыва"""

    # Проверяем, существует ли такой отзыв
    review = Review.is_exists(review_id)
    if not review:
        return "Такого отзыва не существует", 404

    # Проверяем, что админ или создатель отзыва
    if current_user.role != "admin" and current_user.id != review.user_id:
        return "У вас нет прав для этого", 403

    try:
        # Удаляем отзыв из базы данных
        db.session.delete(review)
        db.session.commit()

        # Выводим сообщение об успешном удалении
        flask.flash("Отзыв успешно удален", "success")

    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        db.session.rollback()
        flask.flash(f"Ошибка при удалении отзыва: {str(e)}", "error")
        return f"Ошибка при удалении отзыва: {str(e)}", 500

    # Перенаправляем пользователя на список отзывов
    return redirect(url_for("user_reviews", username=review.user.username))


# --- Работа с авторами ---
@app.route("/authors")
def authors_list():
    """Все авторы"""
    params = {"title": "Авторы",
              "authors": get_all_authors(),
              "local_css_file": "reviews.css"}
    return render_template("all_authors.html", **params)


@app.route("/authors/<int:author_id>")
def author_detail(author_id):
    """Книги автора"""
    author = Author.is_exists_id(author_id)
    if not author:
        return "Такого автора не существует", 404
    params = {"title": f"Книги автора: {author.name} {author.surname}",
              "author": author,
              "local_css_file": "book.css"}
    return render_template("books_author.html", **params)


@app.route("/authors/add_author", methods=["GET", "POST"])
@login_required
def add_author():
    """Функция для добавления автора"""
    if current_user.role != "admin": # Если пользователь не админ
        return "У вас нет прав на это", 403

    form = CreateAuthorForm() # Создаём форму

    params = {"title": "Добавление автора",
              "form": form,
              "local_css_file": "book.css"}

    if form.validate_on_submit():
        # Создаём автора
        try:
            author = Author(name=form.name.data,
                            surname=form.surname.data,
                            patronymic=form.patronymic.data if form.patronymic.data else None)

            # Фиксируем изменения
            db.session.add(author)
            db.session.commit()

            return redirect(url_for("author_detail", author_id=author.id))

        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            print(f"Произошла ошибка: {str(e)}")
            db.session.rollback()
            return "Произошла ошибка при добавлении автора", 500

    return render_template("add_author.html", **params)


@app.route("/authors/change_author/<int:author_id>")
@login_required
def change_author(author_id):
    """Функция для изменения автора"""
    if current_user.role != "admin":  # Если пользователь не админ
        return "У вас нет прав на это", 403

    # Проверяем, существует ли такой автор
    author = Author.is_exists_id(author_id)
    if not author:
        return "Такого автора не существует", 404

    form = CreateAuthorForm(obj=author)  # Создаём форму

    params = {"title": "Добавление автора",
              "form": form,
              "change": "yes", # Флаг для html
              "local_css_file": "book.css"}

    if form.validate_on_submit():
        is_change = False # флаг для изменения

        if form.name.data != author.name:
            author.name = form.name.data
            is_change = True

        if form.surname.data != author.surname:
            author.surname = form.surname.data
            is_change = True

        if form.patronymic.data != author.patronymic:
            author.patronymic = form.patronymic.data
            is_change = True

        if is_change: # Если были сделаны изменения
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return f"Ошибка при сохранении изменений: {str(e)}", 500

        return redirect(url_for("author_detail", author_id=author.id))

    return render_template("add_author.html", **params)


@app.route("/authors/delete_author/<int:author_id>")
@login_required
def delete_author(author_id):
    """Функция для удаления автора"""
    if current_user.role != "admin":  # Если пользователь не админ
        return "У вас нет прав на это", 403

    # Проверяем, существует ли такой автор
    author = Author.is_exists_id(author_id)
    if not author:
        return "Такого автора не существует", 404

    try:
        # Удаляем автора из базы данных
        db.session.delete(author)
        db.session.commit()

        # Выводим сообщение об успешном удалении
        flask.flash("Автор успешно удален", "success")

    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        db.session.rollback()
        flask.flash(f"Ошибка при удалении автора: {str(e)}", "error")
        return f"Ошибка при удалении автора: {str(e)}", 500

    # Перенаправляем пользователя на список авторов
    return redirect(url_for("authors_list"))


# --- Поиск ---
@app.route("/ajax_search")
def ajax_search():
    data = request.args.get("search_request")
    result = search_ajax(data)
    return jsonify(result)


@app.route("/search")
def search():
    page = request.args.get("page")
    search_word = request.args.get("search_word")
    if not page:
        page = 0
    if page < 0:
        return "Такой страницы не существует", 404
    params = {"title": "Лента",
              "books": get_books_for_search(int(page), search_word),
              "max_page": get_max_page(),  # Получаем максимальную страницу
              "current_page": int(page),  # Для отображения текущей страницы
              "local_css_file": "book.css"}
    return render_template("books_ribbon.html", **params)


# --- Пользователь добавляет книгу себе ---
@app.route("/add_book_for_me/<int:book_id>")
@login_required
def add_book_for_me(book_id):
    book = Book.is_exists(book_id)
    if not book:
        return "Такой книги не существует", 404

    add_book = add_book_for_user(book_id, current_user.id)
    if add_book is False:
        flash("Произошла ошибка при добавлении книги, попробуйте позже", "error")
    elif add_book is None:
        flash("Вы уже добавляли эту книгу", "warning")
    else:
        flash("Книга успешно добавлена в вашу библиотеку", "success")

    return redirect(url_for("book_detail", book_id=book.id))
