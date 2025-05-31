from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import date, datetime, timedelta

from db import add_user, add_washing, get_user_data, delete_washing
from sheets_asyn import read_data, insert_data, delete_data, change_status, get_id, delete_row
from states import AddUser, AddEntry, AddEntryToMaster
from messages import create_entry_to_master, create_entry_to_wash, hello_message, hello_message_for_admins

user_router = Router()

ADMIN_LIST = ['list of admins and masters username']

@user_router.message(StateFilter(None), Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.username in ADMIN_LIST:
        buttons = [
            [types.InlineKeyboardButton(text="Журнал стирок", url="https://docs.google.com/spreadsheets/d/17LBXa55bGpy8w4rdPIw0OIKGJmwNDRUFAQjNZWvcL3U/edit?gid=0#gid=0")],
            [types.InlineKeyboardButton(text="Журнал записей к электирку", url="https://docs.google.com/spreadsheets/d/17LBXa55bGpy8w4rdPIw0OIKGJmwNDRUFAQjNZWvcL3U/edit?gid=542977131#gid=542977131")],
            [types.InlineKeyboardButton(text="Журнал записей к плотнику", url="https://docs.google.com/spreadsheets/d/17LBXa55bGpy8w4rdPIw0OIKGJmwNDRUFAQjNZWvcL3U/edit?gid=298556100#gid=298556100")]
            ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(hello_message_for_admins(), reply_markup=keyboard)

    else:
        await state.set_state(AddUser.chat_id)
        await state.update_data(chat_id = message.chat.id)

        await message.answer(hello_message(message.from_user.first_name))
        await message.answer(f"Введи свои фамилию и имя:")

        await state.set_state(AddUser.name)

@user_router.message(AddUser.name, F.text)
async def process_add_data(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Введи номер комнаты:")
    await state.set_state(AddUser.room)

@user_router.message(AddUser.room, F.text)
async def process_select_service(message: types.Message, state: FSMContext):
    await state.update_data(room = message.text)
    data = await state.get_data()
    await state.clear()
    await add_user(data['chat_id'], data['name'], data['room'])

    buttons = [
        [
            types.InlineKeyboardButton(text="Стирка", callback_data="select_washing"),
            types.InlineKeyboardButton(text="Запись к мастеру", callback_data="select_master")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(f"Я запомнил твои данные и буду использовать их для записи. Выбери нужную тебе услугу в моем меню")
    await message.answer(f"Выбери вид услуги:", reply_markup=keyboard)


@user_router.callback_query(F.data == 'select_washing')
async def process_select_day(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="Сегодня", callback_data="choose_machine_today"),
            types.InlineKeyboardButton(text="Завтра", callback_data="choose_machine_tomorrow")
        ],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard= buttons)

    await callback.message.edit_text("Выбери день:", reply_markup = keyboard)

@user_router.callback_query(F.data.startswith('menu'))
async def process_callback_menu(callback: types.CallbackQuery):
    if callback.data == 'menu':
        await callback.message.delete()

    buttons = [
        [
            types.InlineKeyboardButton(text="Стирка", callback_data="select_washing"),
            types.InlineKeyboardButton(text="Запись к мастеру", callback_data="select_master")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f"Выбери вид услуги:", reply_markup=keyboard)

@user_router.callback_query(F.data.startswith('choose_machine_'))
async def process_choose_wmachine(callback: types.CallbackQuery, state: FSMContext):
    action = "choose_time_" + callback.data.split("_")[2]

    if callback.data.split("_")[2] == "today":
        day = "сегодня"
    else:
        day = "завтра"

    buttons = [
        [
            types.InlineKeyboardButton(text="№1", callback_data=f"{action}_1"),
            types.InlineKeyboardButton(text="№2", callback_data=f"{action}_2"),
            types.InlineKeyboardButton(text="№3", callback_data=f"{action}_3")
        ],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(f"Ищу свободные окошки на {day}. Выбери стиральную машину:", reply_markup=keyboard)

@user_router.callback_query(StateFilter(None), F.data.startswith('choose_time_'))
async def process_choose_time(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[2]
    numb_wmachine = callback.data.split("_")[3]
    time_data = await read_data()

    current_date = date.today()
    curr_date_to_str = current_date.strftime("%d.%m.%Y")

    tomorrow_date = date.today() + timedelta(1)
    tom_date_to_str = tomorrow_date.strftime("%d.%m.%Y")

    # current_time = datetime.now()
    # time_from_schedule = datetime.strptime(time_data[i][2], '%H:%M')

    #curr_time_to_str = current_time.strftime("%H:%M")

    # await state.set_state(AddEntry.day)
    # await state.update_data(day=action)

    if action == "today":
        builder = InlineKeyboardBuilder()
        for i in range(0, len(time_data)):
            if time_data[i][0] == numb_wmachine and time_data[i][1] == curr_date_to_str and time_data[i][3] == 'FALSE':
                builder.button(text=f"{time_data[i][2]}",
                               callback_data=f"time_today_{numb_wmachine}_{time_data[i][2]}_{i}")

        if numb_wmachine == "1":
            builder.button(text="Сменить машину", callback_data="choose_time_today_2")
        elif numb_wmachine == "2":
            builder.button(text="Сменить машину", callback_data="choose_time_today_3")
        elif numb_wmachine == "3":
            builder.button(text="Сменить машину", callback_data="choose_time_today_1")

        builder.button(text="Сменить день", callback_data="choose_machine_tomorrow")
        builder.button(text="Вернуться в меню", callback_data="menu")
        builder.adjust(1)

        await callback.message.edit_text(f"Свободные окошки на сегодня для машины №{numb_wmachine}",
                                         reply_markup=builder.as_markup())

    elif action == "tomorrow":
        builder = InlineKeyboardBuilder()
        for i in range(0, len(time_data)):
            if time_data[i][0] == numb_wmachine and time_data[i][1] == tom_date_to_str and time_data[i][3] == 'FALSE':
                builder.button(text=f"{time_data[i][2]}",
                               callback_data=f"time_tomorrow_{numb_wmachine}_{time_data[i][2]}_{i}")

        if numb_wmachine == "1":
            builder.button(text="Сменить машину", callback_data="choose_time_tomorrow_2")
        elif numb_wmachine == "2":
            builder.button(text="Сменить машину", callback_data="choose_time_tomorrow_3")
        elif numb_wmachine == "3":
            builder.button(text="Сменить машину", callback_data="choose_time_tomorrow_1")

        builder.button(text="Сменить день", callback_data="choose_machine_today")
        builder.button(text="Вернуться в меню", callback_data="menu")
        builder.adjust(1)

        await callback.message.edit_text(f"Свободные окошки на завтра для машины №{numb_wmachine}",
                                         reply_markup=builder.as_markup())

@user_router.callback_query(StateFilter(None), F.data.startswith('time_'))
async def process_create_entry(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    await state.set_state(AddEntry.id)
    await state.update_data(id=int(callback.data.split("_")[4]), time=callback.data.split("_")[3],
                            machine=callback.data.split("_")[2], day=callback.data.split("_")[1])

    user_data = await get_user_data(callback.message.chat.id)
    await state.update_data(name=user_data[0])
    await state.update_data(room=user_data[1])

    data = await state.get_data()

    await insert_data(data, 0)

    if data['day'] == 'today':
        current_date = date.today()
        data['day'] = current_date.strftime("%d.%m.%Y")
    else:
        tomorrow_date = date.today() + timedelta(1)
        data['day'] = tomorrow_date.strftime("%d.%m.%Y")

    buttons = [
        [types.InlineKeyboardButton(text="Отменить запись",
                                    callback_data=f"cancel_entry_{data['id']}_{data['day']}_{data['time']}_{data['machine']}")],
        [types.InlineKeyboardButton(text="Подтвердить выполнение", callback_data=f"confirm_{data['id']}")],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data=f"menu_notdelete")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer(create_entry_to_wash(data), reply_markup=keyboard)

    await add_washing(callback.message.chat.id, data['day'], data['time'], data['machine'])

    await state.clear()

@user_router.callback_query(StateFilter(None), F.data.startswith('cancel_entry'))
async def process_delete_entry(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    index = int(callback.data.split("_")[2])
    await delete_data(index)

    day = callback.data.split("_")[3]
    time = callback.data.split("_")[4]
    machine = callback.data.split("_")[5]
    await delete_washing(callback.message.chat.id, day, time, machine)

    buttons = [
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer("Запись отменена!", reply_markup=keyboard)

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

@user_router.callback_query(F.data == 'select_master')
async def process_select_master(callback: types.CallbackQuery):
    buttons = [
        [
            types.InlineKeyboardButton(text="Плотник", callback_data="choose_1"),
            types.InlineKeyboardButton(text="Электрик", callback_data="choose_2")
        ],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard = buttons)

    await callback.message.edit_text("Выбери специалиста:", reply_markup=keyboard)

@user_router.callback_query(StateFilter(None), F.data.startswith('choose_'))
async def process_add_description(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    current_date = date.today()
    curr_date_to_str = current_date.strftime("%d.%m.%Y")

    await state.set_state(AddEntryToMaster.date)
    await state.update_data(date=curr_date_to_str, master=callback.data.split("_")[1])

    if callback.data.split("_")[1] == '1':
        await callback.message.answer("Создаю запись для вызова плотника:")
    elif callback.data.split("_")[1] == '2':
        await callback.message.answer("Создаю запись для вызова электрика:")

    await callback.message.answer("Опиши проблему:")
    await state.set_state(AddEntryToMaster.description)

@user_router.message(AddEntryToMaster.description, F.text)
async def process_add_entry_to_master(message: types.Message, state: FSMContext):
    await state.update_data(description = message.text)

    user_data = await get_user_data(message.chat.id)
    await state.update_data(name=user_data[0])
    await state.update_data(room=user_data[1])

    data = await state.get_data()

    list = int(data['master'])

    id_entry = await get_id(list)

    await state.update_data(id=id_entry)

    data = await state.get_data()

    await insert_data(data, list)

    buttons = [
        [types.InlineKeyboardButton(text="Удалить запись", callback_data=f"delete_entry_{data['id']}_{data['master']}")],
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data=f"menu_notdelete")]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(create_entry_to_master(data), reply_markup = keyboard)

    await state.clear()

@user_router.callback_query(StateFilter(None), F.data.startswith('delete_entry'))
async def process_delete_master_entry(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    index = callback.data.split("_")[2]
    list = int(callback.data.split("_")[3])
    await delete_row(index, list)

    buttons = [
        [types.InlineKeyboardButton(text=f"Вернуться в меню", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer("Запись отменена!", reply_markup=keyboard)
