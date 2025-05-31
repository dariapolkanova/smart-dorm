import asyncio
import gspread_asyncio
import configparser
import json
import os
import time
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'private-key.json'

spreadsheetId = "17LBXa55bGpy8w4rdPIw0OIKGJmwNDRUFAQjNZWvcL3U"

def get_creds():
	return ServiceAccountCredentials.from_json_keyfile_name(
		CREDENTIALS_FILE,
		['https://www.googleapis.com/auth/drive',
		'https://www.googleapis.com/auth/spreadsheets'])

async def read_data():
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    await agc.insert_permission(spreadsheetId, value = 'aguilar28nerha@gmail.com', perm_type = 'user', role = 'writer')
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)
    data = await worksheet.get_values('A2:H61')

    return data

async def compose_range_name(num):
    range_name = 'D' + str(num + 2) + ':' + 'F' + str(num + 2)
    return range_name

async def insert_data(dict, list):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    if list == 0:
        worksheet = await sheet.get_worksheet(list)
        range = await compose_range_name(dict['id'])
        await worksheet.update([['TRUE', dict['name'], dict['room']]], range, False)
    elif list == 1:
        worksheet = await sheet.get_worksheet(list)
        await worksheet.insert_rows([[dict['id'], dict['date'], dict['name'], dict['room'], dict['description']]], 2)
    elif list == 2:
        worksheet = await sheet.get_worksheet(list)
        await worksheet.insert_rows([[dict['id'], dict['date'], dict['name'], dict['room'], dict['description']]], 2)

async def delete_data(index):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)
    range = await compose_range_name(index)
    await worksheet.update([['FALSE', '', '']], range, False)

async def change_status(index):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)
    await worksheet.update([['TRUE']], f"G{index + 2}", False)

async def update_table():
    data = await read_data()

    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)

    for i in range(0, (len(data) // 2)):
        await worksheet.update([[data[i + 30][3], data[i + 30][4], data[i + 30][5], data[i + 30][6]]],
                               f"D{i + 2}:G{i + 2}")
        await delete_data(i + 30)

async def get_id(list):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(list)
    cell = await worksheet.acell('A2')
    if not cell.value:
        id = 1
    else:
        id = int(cell.value) + 1

    return id

async def delete_row(index, list):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(list)

    id_column_values = await worksheet.col_values(1)

    for idx, value in enumerate(id_column_values, start=1):  # start=1 для нумерации строк
        if value == index:
            print(idx, value)
            await worksheet.delete_rows(idx)
            break
