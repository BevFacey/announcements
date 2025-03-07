import requests
import csv
from io import StringIO

def download_text():
    spreadsheet_key = '1SV4eWy58Y6iEIIOGUH60xUZV59eaY7ewp4EoeCZzNxc'
    spreadsheet_gid = '1783949168'
    csv_link = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid={spreadsheet_gid}&format=csv'
    response = requests.get(csv_link)
    response.raise_for_status()
    csv_reader = csv.reader(StringIO(response.text))
    next(csv_reader)  # Skip header row
    text_data = [(row[3], row[4]) for row in csv_reader]
    # write text_data to a file
    with open('text_data.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(text_data)

if __name__ == "__main__":
    download_text()