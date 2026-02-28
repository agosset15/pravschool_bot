space = {" "}
empty = { "!empty!" }
without-name = Без названия
loading = Загрузка...
no = Нет
added = Добавлено

journal-link-text = ·?·

hdr-user = <b>👤 Пользователь:</b>
hdr-error = <b>⚠️ Ошибка:</b>

frg-user-info =
    <blockquote>
    • <b>ID</b>: <code>{ NUMBER($telegram_id, useGrouping: 0) }</code>
    • <b>Имя</b>: { $name } { $username ->
        [0] { empty }
        *[HAS] (<a href="tg://user?id={ $telegram_id }">@{ $username }</a>)
    }
    </blockquote>

ns-student-select =
    { $is_checked ->
        *[0] { $name }
        [1] 🔘 { $name }
    }

today-tomorrow =
    { $today ->
        [1] Сегодня
        *[0] Завтра
    }

week = Неделя
today = Сегодня
tomorrow = Завтра
weekend = Выходной

days =
    .monday = Понедельник
    .tuesday = Вторник
    .wednesday = Среда
    .thursday = Четверг
    .friday = Пятница
    .saturday = Суббота
    .sunday = Воскресенье

months =
    .january = Январь
    .february = Февраль
    .march = Март
    .april = Апрель
    .may = Май
    .june = Июнь
    .july = Июль
    .august = Август
    .september = Сентябрь
    .october = Октябрь
    .november = Ноябрь
    .december = Декабрь

months-possessive =
    .january = января
    .february = февраля
    .march = марта
    .april = апреля
    .may = мая
    .june = июня
    .july = июля
    .august = августа
    .september = сентября
    .october = октября
    .november = ноября
    .december = декабря

inline-ref-btn = 📚 Добавить бота
photos-only-in-bot = <i>Получить фотографию пока можно только в боте</i>
