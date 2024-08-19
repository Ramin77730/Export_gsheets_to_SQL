import gspread
from google.oauth2.service_account import Credentials
import psycopg2

# Путь к вашему файлу учетных данных JSON
credentials_path = 'D:/Рамин/Automation/Google_API/credentials.json'

# Настройка подключения к Google Sheets
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
client = gspread.authorize(credentials)

# Открытие таблицы Google Sheets
spreadsheet = client.open("locations")  # Замените на точное имя таблицы
sheet = spreadsheet.sheet1

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    host="localhost",  # Замените на ваш хост
    database="locations",  # Имя вашей базы данных
    user="postgres",  # Ваше имя пользователя
    password="75495"  # Ваш пароль
)
cursor = conn.cursor()

# Импорт данных из Google Sheets
rows = sheet.get_all_values()[1:]  # Пропустить заголовок
for row in rows:
    point_name, coordinates = row
    latitude, longitude = map(float, coordinates.split(','))
    wkt = f"POINT({longitude} {latitude})"
    cursor.execute(
        "INSERT INTO marks (point_name, point_location) VALUES (%s, ST_GeomFromText(%s))",
        (point_name, wkt)
    )

# Сохранение изменений в базе данных
conn.commit()

# Закрытие соединения с базой данных
cursor.close()
conn.close()

print("Данные успешно импортированы!")