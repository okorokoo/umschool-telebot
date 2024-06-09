import queries
from db import cursor
from bot import bot


def login_required(func):
    def wrapper(message):
        user_id = message.from_user.id
        cursor.execute('SELECT logged_in FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()

        if user and user[0]:  # Если пользователь вошёл в систему
            func(message)
        else:
            bot.reply_to(message, "Для выполнения этой команды необходимо войти в систему.")
    return wrapper


def register_required(func):
    def wrapper(message):
        user_id = message.from_user.id

        is_user_exists = queries.is_user_exists(user_id=user_id)

        if is_user_exists:  # Если пользователь зарегистрирован
            func(message)
        else:
            bot.reply_to(message, "Для выполнения этой команды необходимо зарегистрироваться <b>/register</b>.", parse_mode='html')

    return wrapper
