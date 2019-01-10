#!/usr/bin/python

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('final.json', scope)
client = gspread.authorize(credentials)

content = open('test_csv_file.csv', 'r', encoding='latin-1').read()
# gc.import_csv(wks.id, content)

# The long string is the ID of the spreadsheet called Test
# TEST id is "1uEpTio-0Ub1-ln2HyPjubGaZSHrlR0OX_AnMiXkxMnk"
# Brexit_GBP id is 1Y5oZ125V4T28BEodfZ37owTUo_MO6USQlGihT4W9LyI
client.import_csv("1uEpTio-0Ub1-ln2HyPjubGaZSHrlR0OX_AnMiXkxMnk", content)
# print(wks.get_all_records())
