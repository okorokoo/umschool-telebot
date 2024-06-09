from telebot import types

from bot import bot
import re
import atexit
import auth
import db
from db import SUBJECTS
import queries

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


db.create_db()

NAME_PATTERN = re.compile(r'^[A-Za-zА-Яа-яЁё]+\s[A-Za-zА-Яа-яЁё]+$')

COMMANDS = {
    'Добавить результаты': '/enter_scores',
    'Удалить результаты': '/delete_scores',
    'Просмотреть результаты': '/view_scores',
    'Войти': '/login',
    'Выйти из системы': '/logout',
    'Помощь': '/help',
}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.first_name}!\nЯ бот для добавления и просмотра твоих результатов ЕГЭ.\nЗарегистрируйся <b>/register</b> или войди <b>/login</b>, чтобы начать работу с ботом. Или выбери <b>/help</b> чтобы ознакомиться с командами.",
                     parse_mode='html')


@bot.message_handler(commands=['help'])
def help(message):
    markup = create_commands_keyboard()

    bot.send_message(message.chat.id,
                     f"Я бот для добавления и просмотра твоих результатов ЕГЭ. Выбери команду для работы с ботом.\n"
                     f"""
/register - зарегистрировать пользователя

/login - войти в аккаунт

/enter_scores - ввести результаты

/view_scores - посмотреть результаты

/delete_scores - удалить результаты

/logout - выйти из системы""",
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['register'])
def register(message):
    user_id = message.from_user.id

    is_user_exists = queries.is_user_exists(user_id=user_id)

    if is_user_exists:
        bot.reply_to(message, "Вы уже зарегистрированы. Используйте команду <b>/login</b> для входа.",
                     parse_mode='html')
    else:
        bot.reply_to(message, "Напиши свои имя и фамилию, например <em><b>Иван Иванов</b></em>", parse_mode='html')
        bot.register_next_step_handler(message, get_name)


@bot.message_handler(commands=['login'])
@auth.register_required
def login(message):
    user_id = message.from_user.id

    db.cursor.execute('SELECT first_name, last_name, logged_in FROM users WHERE user_id = ?', (user_id,))
    user = db.cursor.fetchone()

    if user:
        if user[2]:
            bot.reply_to(message, f"Вы уже вошли в систему как {user[0]} {user[1]}.")
        else:
            bot.reply_to(message, "Введите пароль: ")
            bot.register_next_step_handler(message, check_password, user[0], user[1])


@bot.message_handler(commands=['logout'])
@auth.register_required
@auth.login_required
def logout(message):
    user_id = message.from_user.id

    queries.set_user_logged_out(user_id=user_id)
    bot.reply_to(message, f"Вы вышли из системы!")


@bot.message_handler(commands=['enter_scores'])
@auth.login_required
def enter_scores(message):
    user_id = message.from_user.id

    markup = create_subjects_keyboard(user_id=user_id)
    bot.reply_to(message, "Выбери предмет, который хочешь добавить:", reply_markup=markup)


@bot.message_handler(commands=['view_scores'])
@auth.login_required
def view_scores(message):
    user_id = message.from_user.id

    scores = queries.view_all_scores(user_id=user_id)

    if scores:
        string = ''

        for i in range(len(scores)):
            string += f'''{scores[i][0]} - {scores[i][1]}\n'''

        bot.reply_to(message, string)

    else:
        bot.reply_to(message, "Вы пока не добавили никаких результатов. Выберите <b>/enter_scores</b>, чтобы добавить.", parse_mode='html')


@bot.message_handler(commands=['delete_scores'])
@auth.login_required
def delete_score(message):
    user_id = message.from_user.id

    scores = queries.view_all_scores(user_id=user_id)

    if scores:
        subjects = [score[0] for score in scores]

        markup = delete_subjects_keyboard(subjects=subjects)

        bot.reply_to(message, "Выбери предмет, результаты которого хочешь удалить:", reply_markup=markup)

    else:
        bot.reply_to(message, "Вы пока не добавили никаких результатов. Выберите <b>/enter_scores</b>, чтобы добавить.",
                     parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data.startswith('subject_'))
@auth.login_required
def handle_subject_callback(call):
    subject_name = call.data[len('subject_'):]
    bot.send_message(call.message.chat.id, f"Вы выбрали {subject_name}. Введите ваш результат:")
    bot.register_next_step_handler(call.message, get_score, call.from_user.id, subject_name)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
@auth.login_required
def handle_delete_subject_callback(call):
    subject_name = call.data[len('delete_'):]
    user_id = call.from_user.id

    subject_id = queries.get_subject_id_by_name(subject_name=subject_name)

    queries.delete_score(user_id=user_id, subject_id=subject_id)

    bot.send_message(call.message.chat.id, f"Результаты по предмету {subject_name} удалены!")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


@bot.message_handler(func=lambda message: message.text in COMMANDS.keys())
def handle_command(message):
    command = message.text
    if command == 'Добавить результаты':
        enter_scores(message)
    elif command == 'Удалить результаты':
        delete_score(message)
    elif command == 'Просмотреть результаты':
        view_scores(message)
    elif command == 'Войти':
        login(message)
    elif command == 'Выйти из системы':
        logout(message)
    elif command == 'Помощь':
        help(message)


@bot.message_handler()
def choose_command(message):
    markup = create_commands_keyboard()

    bot.reply_to(message, f"Выберите команду:",
                 reply_markup=markup)


def get_score(message, user_id, subject_name):
    markup = create_commands_keyboard()

    score = message.text
    subject_id = queries.get_subject_id_by_name(subject_name=subject_name)

    queries.add_score(user_id=user_id, subject_id=subject_id, score=score)

    bot.reply_to(message, f"Результаты к предмету {subject_name} сохранены!", reply_markup=markup)


def get_name(message):
    if not NAME_PATTERN.match(message.text):
        bot.reply_to(message, "Пожалуйста, введите свои имя и фамилию, например <em><b>Иван Иванов</b></em>",
                     parse_mode='html')
        bot.register_next_step_handler(message, get_name)
        return

    user_first_name, user_last_name = message.text.split(' ', 1)

    bot.reply_to(message, "Введите пароль для вашей учётной записи:")
    bot.register_next_step_handler(message, get_password, user_first_name, user_last_name)


def get_password(message, user_first_name, user_last_name):
    user_id = message.from_user.id
    user_password = generate_password_hash(message.text)

    # Сохранение пользователя
    if queries.store_user(user_id=user_id, user_first_name=user_first_name, user_last_name=user_last_name,
                          user_password=user_password):

        bot.reply_to(message,
                     f"Спасибо! Ваше имя: <em><b>{user_first_name}</b></em>, ваша фамилия: <em><b>{user_last_name}</b></em>. Войдите <b>/login</b> в систему.",
                     parse_mode='html')
    else:
        bot.reply_to(message, "Произошла ошибка при сохранении данных. Попробуйте снова.")
        bot.register_next_step_handler(message, get_name)


def check_password(message, user_first_name, user_last_name):
    markup = create_commands_keyboard()

    user_id = message.from_user.id
    password_hash = queries.get_hash(user_id=user_id)

    password = message.text

    if check_password_hash(password_hash, password):
        queries.set_user_logged_in(user_id=user_id)
        bot.reply_to(message, f"Добро пожаловать, {user_first_name} {user_last_name}! Выберите команду:", reply_markup=markup)
    else:
        bot.reply_to(message, "Неверный пароль. Попробуйте снова.")
        bot.register_next_step_handler(message, check_password, user_first_name, user_last_name)


def create_subjects_keyboard(user_id: int):
    markup = types.InlineKeyboardMarkup()

    scores = queries.view_all_scores(user_id=user_id)

    added_subjects = [score[0] for score in scores]

    subjects = [subject for subject in SUBJECTS if subject not in added_subjects]

    for subject in subjects:
        markup.add(types.InlineKeyboardButton(subject, callback_data=f'subject_{subject}'))
    return markup


def delete_subjects_keyboard(subjects: list[str]):
    markup = types.InlineKeyboardMarkup()
    for subject in subjects:
        markup.add(types.InlineKeyboardButton(subject, callback_data=f'delete_{subject}'))
    return markup


def create_commands_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for command in COMMANDS:
        markup.add(types.KeyboardButton(command))
    return markup


def create_login_button():
    markup = types.InlineKeyboardMarkup()
    login_button = types.InlineKeyboardButton('Войти', callback_data='login')
    markup.add(login_button)
    return markup


bot.infinity_polling()


# Закрытие соединения с базой данных при завершении работы скрипта
def close_db_connection():
    db.cursor.close()
    db.conn.close()


atexit.register(close_db_connection)
