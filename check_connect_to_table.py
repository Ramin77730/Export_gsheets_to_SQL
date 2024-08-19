import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from gspread.exceptions import SpreadsheetNotFound, APIError

# Укажите путь к вашему файлу credentials.json
CREDENTIALS_FILE = 'D:\Рамин\Automation\Google_API\credentials.json'

# Название таблицы, которую нужно проверить
SPREADSHEET_NAME = 'locations'

def check_access():
    try:
        # Загрузка учетных данных
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )

        # Авторизация и создание клиента gspread
        client = gspread.authorize(credentials)

        # Попытка открыть таблицу по названию
        spreadsheet = client.open(SPREADSHEET_NAME)
        print(f"Доступ к таблице '{SPREADSHEET_NAME}' получен успешно.")

    except SpreadsheetNotFound:
        print(f"Таблица с названием '{SPREADSHEET_NAME}' не найдена или у вас нет к ней доступа.")
    except APIError as e:
        if e.response.status_code == 403:
            print("Доступ запрещен: проверьте, есть ли у вас необходимые права для доступа к таблице.")
        else:
            print(f"Произошла ошибка при попытке доступа к таблице: {e}")

if __name__ == '__main__':
    check_access()
