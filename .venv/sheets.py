import httplib2
import apiclient.discovery
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime, timedelta

CREDENTIALS_FILE = 'private-key.json'  # имя файла с закрытым ключом

spreadsheetId = "17LBXa55bGpy8w4rdPIw0OIKGJmwNDRUFAQjNZWvcL3U"

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth)
shareRes = driveService.permissions().create(
    fileId = spreadsheetId,
    body = {'type': 'user', 'role': 'writer', 'emailAddress': 'aguilar28nerha@gmail.com'},  # доступ на чтение кому угодно
    fields = 'id'
).execute()

def read_data(): #service, spreadsheet_id, range_name
    range_name = "A2:H19"
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheetId, range=range_name).execute()
    values = result.get('values', [])
    free_windows = [[]]
    if not values:
        print('No data found.')
    else:
        for row in values:
            if row[3] == '0':
                free_windows.append(row)
    free_windows.pop(0)
    return free_windows

def compose_range_name(num):
    range_name = 'D' + str(num + 1) + ':' + 'F' + str(num + 1)
    return range_name

def insert_data(service, spreadsheet_id, range_name, name, room):
    body = {
        'values': [["1", name, room]]
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption="USER_ENTERED", body=body).execute()
    print(f'{result.get("updatedCells")} cells updated.')



#data = read_data() #service, spreadsheetId, "A2:H19"
# current_date = date.today() + timedelta(1)
# date = current_date.strftime("%d.%m.%Y")
# print(date)
# for row in data:
#     #date = datetime.strptime(row[1], '%d.%m.%Y')
# date = current_date.strftime("%d.%m.%Y")
#     #print(date, ' ', current_date, ' ', date2, ' ', row[1])
#     #print(current_date)
#     if date == row[1]:
#         print(row)
#range_name = compose_range_name(14)
#print(range_name)
#insert_data(service, spreadsheetId, range_name, "Игорь", "100")
