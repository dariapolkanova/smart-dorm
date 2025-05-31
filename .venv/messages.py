def hello_message(name):
    MESSAGE = (
        f'Привет, {name}!\n\n'
        'Я бот "Умное общежитие". С моей помощью ты сможешь\n'
        'записаться на стирку или вызвать мастера, если у тебя\n'
        'что-то сломалось.\n'
    )

    return MESSAGE

def hello_message_for_admins():
    MESSAGE = (
        f'Добро пожаловать в "Умное общежитие"!\n\n'
        'Здесь вам будут доступны журналы записей студентов в постирочную и к мастерам.\n\n'
        'Выберите необходимый журнал в меню ниже.'
    )

    return MESSAGE


def create_entry_to_master(data):
    if data['master'] == '1':
        data['master'] = 'плотник'
    elif data['master'] == '2':
        data['master'] = 'электрик'

    ENTRY = ("Запись добавлена в журнал\n"
            "\n"
            f"Дата обращения: {data['date']}\n"
            f"Студент: {data['name']}\n"
            f"Номер комнаты: {data['room']}\n"
            f"Описание проблемы: {data['description']}\n"
            f"Мастер: {data['master']}")

    return ENTRY


def create_entry_to_wash(data):
    ENTRY = (f"Я записал тебя на стирку на {data['day']} в {data['time']}; "
             f"Номер машины: {data['machine']}")

    return ENTRY