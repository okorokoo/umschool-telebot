# umschool-telebot

umschool-telebot — это Телеграм-бот для добавления и просмотра результатов ЕГЭ.

## Функции

- Добавление результатов ЕГЭ
- Просмотр результатов ЕГЭ
- Удаление результатов ЕГЭ

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/okorokoo/umschool-telebot.git
   cd umschool-telebot
   ```

2. Установите необходимые пакеты:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

1. Настройте токен Телеграм-бота:
   - Создайте файл `.env` в корневой директории.
   - Добавьте ваш токен Телеграм-бота в файл `.env`:
     ```plaintext
     API_TOKEN=ваш_токен
     ```

2. Запустите бота:
   ```bash
   python main.py
   ```

## Файлы

- `main.py`: Основной скрипт для запуска бота.
- `auth.py`: Обработка аутентификации пользователей.
- `bot.py`: Команды и обработчики бота.
- `constants.py`: Хранение постоянных значений, используемых в боте.
- `db.py`: Управление операциями базы данных.
- `queries.py`: Функции запросов к базе данных.
- `requirements.txt`: Список зависимостей.