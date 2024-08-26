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
spreadsheet = client.open("Data_1")
sheet = spreadsheet.sheet1

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="locations",
    user="postgres",
    password="75495"
)
cursor = conn.cursor()

# Получение заголовков и данных
headers = sheet.row_values(1)  # Первая строка (заголовки)
rows = sheet.get_all_values()[1:]  # Остальные строки с данными

# Функция для обработки пустых ячеек
def process_value(value):
    if value == '':
        return None  # Если ячейка пуста, возвращаем None
    return value

# Вставка данных из Google Sheets в таблицу PostgreSQL
for row in rows:
    # Преобразование всех значений строки, включая обработку пустых ячеек
    processed_row = [process_value(value) for value in row]

    # Преобразование координат в формат POINT
    if processed_row[-1]:  # Проверяем, что координаты не пусты
        lat, lon = processed_row[-1].split(",")  # Разделяем широту и долготу
        coordinates = f"POINT({lon.strip()} {lat.strip()})"  # Форматируем в POINT
    else:
        coordinates = None

    # Обновление строки для вставки данных, включая новый столбец photo_5 и координаты
    cursor.execute("""
        INSERT INTO data_1 (
            name, voltage, length_1, length_2, length_3, length_4, length_5,
            width_1, width_2, width_3, photo_1, photo_2, photo_3, photo_4, photo_5, coordinates
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
    """, (*processed_row[:-1], coordinates))  # Все значения строки, кроме последнего, и преобразованные координаты

# Сохранение изменений
conn.commit()

# Проверка количества записей в таблице
cursor.execute("SELECT COUNT(*) FROM data_1")
count = cursor.fetchone()[0]
print(f"Количество записей в таблице data_1 после вставки всех строк: {count}")

# Закрытие соединения с базой данных
cursor.close()
conn.close()
