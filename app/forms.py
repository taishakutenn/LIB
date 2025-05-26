"""Файл для Форм"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, EmailField, RadioField, BooleanField, TextAreaField
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets.core import ListWidget, CheckboxInput


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 50)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    role = RadioField("Выберите роль",
                      choices=[("admin", "Админ"), ("user", "Пользователь")],
                      default="user",
                      validators=[DataRequired()]
                      )
    admin_code = PasswordField("Для создания админского аккаунта введите код")
    password = PasswordField("Пароль",
                             validators=[DataRequired(), Length(6, 25),
                                         EqualTo('confirm_password', message='Пароли не совпадают')])
    confirm_password = PasswordField("Повторите пароль")
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class AuthorForm(FlaskForm):
    """Доп. форма для создания динамечкого поля в форме для авторов"""
    class Meta:
        csrf = False  # отключаем CSRF для вложенной формы
    name = StringField("Введите ФИО автора (через пробел)")


class AddBookForm(FlaskForm):
    title = StringField("Название книги", validators=[DataRequired(), Length(3, 98)])
    description = StringField("Описание книги", validators=[DataRequired(), Length(min=10)])
    link_to_download = StringField("Ссылка на скачивание")
    book_photo = FileField("Обложка книги")
    authors = FieldList(FormField(AuthorForm), min_entries=1) # Минимум 1 поле для автора
    tags = MultiCheckboxField("Теги", choices=[])  # choices зададим в маршруте


class CreateReviewForm(FlaskForm):
    title = StringField("Заголовок отзыва", validators=[DataRequired(), Length(10, 254)])
    text = TextAreaField("Текст отзыва", validators=[DataRequired(), Length(min=50)])


class CreateAuthorForm(FlaskForm):
    name = StringField("Имя автора", validators=[DataRequired(), Length(3, 50)])
    surname = StringField("Фамилия автора", validators=[DataRequired(), Length(3, 50)])
    patronymic = StringField("Отчество автора (если есть)", validators=[Length(0, 73)])
