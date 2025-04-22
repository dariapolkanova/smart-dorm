from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import date, datetime, timedelta
from sheets_asyn import read_data, insert_data, delete_data, change_status

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    buttons = [
        [
            types.InlineKeyboardButton(text="Стирка", callback_data="select_washing"),
            types.InlineKeyboardButton(text="Запись к мастеру", callback_data="select_not_washing")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard= buttons)
    await message.answer(f"Привет, {message.from_user.first_name}! Выбери вид услуги:", reply_markup = keyboard)

@user_router.callback_query(F.data == 'select_washing')
async def process_select_service(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="Записаться", callback_data="sign_up_for_laundry")
        ],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard= buttons)

    await callback.message.answer("Выбери действие:", reply_markup = keyboard)

@user_router.callback_query(F.data == 'sign_up_for_laundry')
async def process_select_service(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="Сегодня", callback_data="choose_time_today"),
            types.InlineKeyboardButton(text="Завтра", callback_data="choose_time_tomorrow")
        ],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard= buttons)

    await callback.message.answer("Выбери день:", reply_markup = keyboard)

@user_router.callback_query(F.data == 'menu')
async def process_callback_menu(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="Стирка", callback_data="select_washing"),
            types.InlineKeyboardButton(text="Запись к мастеру", callback_data="select_not_washing")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f"Выбери вид услуги:", reply_markup=keyboard)

class AddEntry(StatesGroup):
    id = State()
    day = State()
    machine = State()
    time = State()
    name = State()
    room = State()

@user_router.callback_query(StateFilter(None), F.data.startswith('choose_time_'))
async def process_choose_time(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[2]
    time_data = await read_data()

    current_date = date.today()
    curr_date_to_str = current_date.strftime("%d.%m.%Y")

    tomorrow_date = date.today() + timedelta(1)
    tom_date_to_str = tomorrow_date.strftime("%d.%m.%Y")

    # await state.set_state(AddEntry.day)
    # await state.update_data(day=action)

    if action == "today":
        builder = InlineKeyboardBuilder()
        count = 0
        for i in range(0, len(time_data)):
            if time_data[i][1] == curr_date_to_str and time_data[i][3] == '0':
                builder.button(text=f"№{time_data[i][0]}  {time_data[i][2]}",
                               callback_data=f"time_{i}_{time_data[i][2]}_{time_data[i][0]}_today")
                count = count + 1

        builder.button(text="Сменить день", callback_data="choose_time_tomorrow")
        builder.button(text="Вернуться в меню", callback_data="menu")
        builder.adjust(4, 2)

        await callback.message.answer("Свободные окошки на сегодня", reply_markup=builder.as_markup())

    elif action == "tomorrow":
        builder = InlineKeyboardBuilder()
        count = 0
        for i in range(0, len(time_data)):
            if time_data[i][1] == tom_date_to_str and time_data[i][3] == '0':
                builder.button(text=f"№{time_data[i][0]}  {time_data[i][2]}",
                               callback_data=f"time_{i}_{time_data[i][2]}_{time_data[i][0]}_tomorrow")
                count = count + 1

        builder.button(text="Сменить день", callback_data="choose_time_today")
        builder.button(text="Вернуться в меню", callback_data="menu")
        builder.adjust(4, 2)

        await callback.message.answer("Свободные окошки на завтра", reply_markup=builder.as_markup())

@user_router.callback_query(StateFilter(None), F.data.startswith('time_'))
async def process_request_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    await state.set_state(AddEntry.id)
    await state.update_data(id=int(callback.data.split("_")[1]), time=callback.data.split("_")[2],
                            machine=callback.data.split("_")[3], day=callback.data.split("_")[4])

    await callback.message.answer("Введи свою фамилию и имя:")
    await state.set_state(AddEntry.name)

@user_router.message(AddEntry.name, F.text)
async def process_add_name(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Введи номер комнаты:")
    await state.set_state(AddEntry.room)

@user_router.message(AddEntry.room, F.text)
async def process_add_name(message: types.Message, state: FSMContext):
    await state.update_data(room = message.text)
    data = await state.get_data()

    buttons = [
        [types.InlineKeyboardButton(text="Удалить запись", callback_data=f"cancel_entry_{data['id']}")],
        [types.InlineKeyboardButton(text="Подтвердить выполнение", callback_data=f"confirm_{data['id']}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await insert_data(data)
    if data['day'] == 'today':
        current_date = date.today()
        data['day'] = current_date.strftime("%d.%m")
    else:
        tomorrow_date = date.today() + timedelta(1)
        data['day'] = tomorrow_date.strftime("%d.%m")
    await message.answer(f"Я записал тебя на стирку на {data['day']} в {data['time']};"
                         f"номер машины: {data['machine']}", reply_markup = keyboard)
    await state.clear()

@user_router.callback_query(StateFilter(None), F.data.startswith('cancel_entry'))
async def process_delete_entry(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    index = int(callback.data.split("_")[2])
    await delete_data(index)


    buttons = [
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer("Запись удалена!", reply_markup=keyboard)

@user_router.callback_query(StateFilter(None), F.data.startswith('confirm_'))
async def process_confirm_entry(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    index = int(callback.data.split("_")[1])
    await change_status(index)

    buttons = [
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer("Задача выполнена!", reply_markup=keyboard)
