msg-main-menu =
    👋 Привет, { $name }!
    { $is_teacher ->
        *[0] Вы в { $grade } классе.
        [1] Вы учитель. { $grade }
    }

    Выберите день из кнопок внизу, или
    Выберите действие:

msg-netschool-menu =
    Текущая неделя: <b>{ $week }</b>

    Выберите день, или поменяте неделю:

msg-netschool-day =
    Для ученика <b>{ $student_name }</b>:

    { $day_text }

    { $children ->
        [0] { space }
        *[HAS]Выберите ребенка:
}

journal-assignment =
    { $is_duty ->
        [1] ⚠️ДОЛГ!
       *[0] { space }
    }
    <b>{ $subject }</b>({ $type }) <a href="{ $link }">{ journal-link-text }</a>
    { $content }{ $mark ->
        [0] { empty }
       *[HAS]  -- <b>{ $mark }</b>
    }

journal-no-assignments = <b>{ $subject }</b>
    Заданий нет.

journal-overdue = Вот ваши долги на данное время:

journal-duty = { $assignment_type } по предмету { $subject } <a href="{ $link }">{ journal-link-text }</a>
    { $content }

no-overdue-assignments = На данный момент просроченных заданий нет!

msg-dashboard = <b>Админ-панель</b>
    Выберите действие:

msg-add-schedule = Загрузите файл расписания (.xlsx)
    Формат файла должен соответствовать шаблону.

msg-add-photo = Загрузите фото с расписанием на год
    Это фото будет отображаться при запросе годового расписания.

msg-user-dashboard = Панель пользователя
    Выберите действие:

msg-rooms-menu = Кабинеты
    Выберите действие:

msg-rooms =
    .select-day = Выберите день недели:

msg-settings-menu = Настройки
    Выберите действие:

msg-ns-credentials =
    .login = Введите логин от электронного журнала:
    .password = Введите пароль от электронного журнала:

msg-register-grade = Выберите ваш класс из списка или введите его название:
    Используйте inline-режим для поиска.