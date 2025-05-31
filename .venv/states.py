from aiogram.fsm.state import State, StatesGroup

class AddUser(StatesGroup):
    chat_id = State()
    name = State()
    room = State()

class AddEntry(StatesGroup):
    id = State()
    day = State()
    machine = State()
    time = State()
    name = State()
    room = State()

class AddEntryToMaster(StatesGroup):
    id = State()
    date = State()
    name = State()
    room = State()
    description = State()
    master = State()