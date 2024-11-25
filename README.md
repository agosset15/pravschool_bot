# Бот-расписание уроков

[<img src="https://img.shields.io/badge/Telegram-%40pravschool__bot-blue">](https://t.me/pravschool_bot)
[<img src="https://img.shields.io/badge/автор-связаться-blue">](https://t.me/ag15bots)

Телеграмм-бот, в которым можно посмотреть расписание Свято-Димитриевской школы.

![Пример](https://github.com/agosset15/pravschool_bot/assets/100594613/e6eb4912-256a-4649-8d04-23e67c119166 "Пример работы бота")


## Реализованные функции:
* Изменение расписания прямо в боте с соответствующим exel-файлом
* Админ-панель для выявления ошибок в базе данных, и исправления их без нарушения работе бота
* Просмотр расписания на год/неделю
* Улучшенная система работы с базой данных
* Удаленное подключение к электронному журналу для получения домашнего задания, оценок и долгов.
* Inline-режим работы с возможностью доступа к ЭЖ
* Веб-приложение, как альтернативный интерфейс для работы с ботом.

## Технологии

* [aiogram](https://github.com/aiogram/aiogram) — работа с Telegram Bot API;
* [MySQL](https://www.mysql.com/) — перманентное хранение данных;
* [Redis](https://redis.io/) - временное хранение сессий и состояний;
* [aiohttp](https://aiohttp.org/) — веб-сервер для веб-приложения;
* [sqlalchemy](https://sqlalche.me/) - "прослойка" между базой данных и ботом

## Установка


<details>
<summary>Вариант с systemd</summary>

1. Скопируйте файл `env_example` как `.env` (с точкой в начале), откройте и отредактируйте содержимое.
2. Выполните `python3 -m pip install -r requirements.txt`
3. Используйте Systemd, пример службы есть в репозитории. Вот <a href="https://telegra.ph/Sozdanie-servisa-09-21" target="_blank">статья</a> для ознакомления.
</details>

<details>
<summary>Вариант с docker (легкий)</summary>

1. На вашем устройстве должен быть установлен docker
2. Выполните `docker pull agosset15/pravschool_bot` а затем `docker run agosset15/pravschool_bot:v1`
</details>

## Благодарности

* [@KiberHack](https://t.me/KiberHack) за идею, и частичную реализацию `db.py`, за поддержку проблемных ситуациях.
* [Anonim] за изначальный вектор направления.
* Проспонсировать дальнейшие разработки можно по [ссылке](https://yoomoney.ru/to/4100117410709216)
