event-user =
    .registered =
    #UserRegistered
    <b>Новый пользователь!</b>

    { frg-user-info }

event-error =
    .general =
        #ErrorEvent
        <b>Произошла ошибка!</b>

        { $telegram_id ->
        [0] { space }
        *[HAS]
        { hdr-user }
        { frg-user-info }
        }

        { hdr-error }
        <blockquote>
        { $error }
        </blockquote>

ntf-error =
    .unknown = ⚠️ <i>Произошла ошибка.</i>
    .permission-denied = ⚠️ <i>У вас недостаточно прав.</i>
    .lost-context-restart = ⚠️ <i>Произошла ошибка. Диалог перезапущен.</i>
    .year-missed = Расписание на год не найдено.
    .already-admin = Вы уже являетесь администратором.
    .incorrect-credentials = Неверные логин или пароль.
    .not-found = Не найдено.
    .parsig = ⚠️ <i>Произошла ошибка.</i>

        <blockquote>
        { $error }
        </blockquote>

ntf-success =
    .parser = Расписание успешно загружено!

ntf-registration = Регистрация >>

ntf-schedule=
    .no-schedule = ⚠️ У вас нет расписания.
    .not-found = Расписание не найдено.
    .weekend = { today-tomorrow } выходной!

    .day = <b>{ $day }:</b>

        { $text }

    .today = <b>Расписание на сегодня:</b>

        { $text }
    .tomorrow = <b>Расписание на завтра:</b>

        { $text }
    .week = <b>Расписание на неделю:</b>

        { $text }
    .free-rooms = <b>{ $day }, свободные кабинеты:</b>

        { $text }

ntf-become-admin = Вы можете помочь развитию бота и своим одноклассникам или ученикам, добавляя домашние задания напрямую в бота, в случае затруднений в работе с электронным журналом.
Для этого надо получить специальное разрешение, написав: { $owner }

err-not-registered =
    .title = Нет регистрации
    .description = Пожалуйста, зарегистрируйтесь, чтобы использовать inline-режим