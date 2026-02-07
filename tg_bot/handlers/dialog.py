from datetime import datetime, timedelta
from aiogram import F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.scene import After, Scene, on
from aiogram.fsm.context import FSMContext


from tg_bot.models import User
from tg_bot.states import NSChild, GetNS
from tg_bot.keyboards import inline_kb, settings_kb, ns_kb
from tg_bot.utils.ns import get_ns_object, NoResponseFromServer, NSError, get_ns_day
from tg_bot.config import days


class DefaultScene(Scene):

    @on.message.enter()
    @on.callback_query(F.data == "ns")
    async def main_handler(self, call: CallbackQuery, state: FSMContext, user: User):
        if user.is_ns:
            start = datetime.now() - timedelta(days=datetime.now().weekday())
            end = start + timedelta(days=6)
            text = (f"Выберете день на который вы хотите посмотреть домашнее задание из электронного журнала\n"
                    f"Текущая неделя: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")
            await state.set_state(GetNS.day)
            await state.update_data(start=start.strftime('%d.%m.%Y'), end=end.strftime('%d.%m.%Y'))
            await self.wizard.update_data(start=start.strftime('%d.%m.%Y'), end=end.strftime('%d.%m.%Y'))
            if call.message.photo:
                await call.message.delete()
                return await call.message.answer(text, reply_markup=ns_kb())
            return await call.message.edit_text(text, reply_markup=ns_kb())
        else:
            return await call.answer("Вы не ввели свои данные. Введите их в меню настроек.", show_alert=True)

    @on.message(GetNS.day, F.data.contains("week"))
    async def week(self, call: CallbackQuery):
        td = timedelta(days=7)
        if call.data == 'back_week':
            td = -td
        data = await self.wizard.get_data()
        start = datetime.strptime(data.get("start"), '%d.%m.%Y')
        end = datetime.strptime(data.get("end"), '%d.%m.%Y')
        start = (start + td).strftime('%d.%m.%Y')
        end=(end + td).strftime('%d.%m.%Y')
        await self.wizard.update_data(start=start, end=end)
        await call.message.edit_text(f"Выберете день на который вы хотите посмотреть домашнее задание из "
                                     f"электронного журнала\nТекущая неделя: {start} - {end}", reply_markup=ns_kb())

    @on.message(GetNS.day, F.data.in_([range(len(days))]), after=After.exit())
    async def day_handler(self, call: CallbackQuery, state: FSMContext, user: User, bot: Bot):
        data = await self.wizard.get_data()
        start = datetime.strptime(data['start'], '%d.%m.%Y')
        day = int(call.data.strip('day'))
        await state.update_data(day=day)
        try:
            ns = await get_ns_object(user)
            text = await get_ns_day(start, day, bot, ns)
        except NoResponseFromServer as e:
            return await call.message.answer(' '.join(e.__notes__),
                                             reply_markup=inline_kb(**{call.data: "Повторить попытку"}))
        except NSError as e:
            return await call.message.answer(' '.join(e.__notes__), reply_markup=settings_kb())
        if len(ns.students) > 1:
            await state.set_state(NSChild.day)
            await state.update_data(ns=ns, day=day, start=data['start'])
            return await call.message.answer(
                f"Для ребенка {ns.students[0]['nickName']}:\n\n" + text + '\n\nВыберите ребенка:',
                reply_markup=inline_kb(
                    **{i: child['nickName'] for i, child in enumerate(ns.students)}),
                disable_web_page_preview=True)
        await state.clear()
        await call.message.answer(text, disable_web_page_preview=True)
