import asyncio
import gspread_asyncio
import configparser
import json
import os
import time
from oauth2client.service_account import ServiceAccountCredentials
import gspread

CREDENTIALS_FILE = '.venv/private-key.json'

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

async def insert_data(dict):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)
    range = await compose_range_name(dict['id'])
    await worksheet.update([['1', dict['name'], dict['room']]], range)

async def delete_data(index):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)
    range = await compose_range_name(index)
    await worksheet.update([['0', '', '']], range)

async def change_status(index):
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    sheet = await agc.open_by_key(spreadsheetId)
    worksheet = await sheet.get_worksheet(0)
    await worksheet.update([['1']], f"G{index + 2}")

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




# agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
# asyncio.run(update_table())