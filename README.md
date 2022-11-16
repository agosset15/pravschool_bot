# Бот-расписание уроков

[<img src="https://img.shields.io/badge/Telegram-%40pravschool__bot-blue">](https://t.me/pravschool_bot)
[<img src="https://img.shields.io/badge/автор-связаться-blue">](https://t.me/agosset15)

Телеграмм-бот, в которым можно посмотреть расписание Свято-Димитриевской школы.

## Реализованные функции:
* Изминения расписания напрямую через бота с сообветствующим exel-файлом
* Админ-панель для выявления ошибок в базе данных, и исправления их без нарушения работв бота
* Просмотр расписания на год/неделю
* Улучшенная система работы с базой данных
* И конечно, возможности расширения, и улучшения

## Технологии

* [aiogram](https://github.com/aiogram/aiogram) — работа с Telegram Bot API;
* [sqlite3](https://docs.python.org/3/library/sqlite3.html) — перманентное хранение данных;
* Systemd

## Установка

1. Скопируйте файл `env_example` как `.env` (с точкой в начале), откройте и отредактируйте содержимое.
2. Выполните `python -m pip install -r requirements.txt`
3. Используйте Systemd, пример службы есть в репозитории. Вот <a href="https://telegra.ph/Sozdanie-servisa-09-21" target="_blank">статья</a> для ознакомления.

## Благодарности

* [@KiberHack](https://t.me/KiberHack) за идею, и частичную реализацию `db.py`, за поддержку проблемных ситуациях.
* [Anonim] за изначальный вектор направления.
