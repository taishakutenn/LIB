"""Файл для Форм"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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
