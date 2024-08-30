import gspread
from google.oauth2.service_account import Credentials
import psycopg2
from urllib.parse import urlparse, parse_qs

# Путь к вашему файлу учетных данных JSON
credentials_path = r'R:\Мой диск\Google_API\credentials.json'

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

# Функция для извлечения ID из ссылки на Google Диск
def extract_drive_id(url):
    parsed_url = urlparse(url)
    if 'drive.google.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        if 'id' in query_params:
            return query_params['id'][0]
        elif parsed_url.path.startswith('/file/d/'):
            return parsed_url.path.split('/')[3]
    return url  # Возвращаем оригинальное значение, если не удалось извлечь ID

# Функция для проверки, является ли строка числом
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Вставка данных из Google Sheets в таблицу PostgreSQL
for row in rows:
    # Преобразование всех значений строки, включая обработку пустых ячеек
    processed_row = [process_value(value) for value in row]

    # Извлечение ID для фотографий
    for i in range(10, 15):  # Предположим, что фото хранятся в столбцах с 11 по 15
        if processed_row[i]:
            processed_row[i] = extract_drive_id(processed_row[i])

    # Преобразование координат в формат POINT
    coordinates_str = processed_row[-3].strip()  # Корректируем индекс для координат
    if coordinates_str and "," in coordinates_str:  # Проверяем, что координаты не пусты и содержат запятую
        lat, lon = coordinates_str.split(",", 1)  # Разделяем только по первой запятой
        if is_float(lat) and is_float(lon):  # Проверяем, что широта и долгота - числа
            coordinates = f"POINT({lon.strip()} {lat.strip()})"  # Форматируем в POINT
        else:
            print(f"Неверный формат координат: '{coordinates_str}'. Пропуск строки.")
            continue
    else:
        print(f"Неверный формат координат: '{coordinates_str}'. Пропуск строки.")
        continue

    # Обновление строки для вставки данных, включая координаты
    cursor.execute("""
        INSERT INTO data_1 (
            name, voltage, length_1, length_2, length_3, length_4, length_5,
            width_1, width_2, width_3, photo_1, photo_2, photo_3, photo_4, photo_5, coordinates, comments, date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326), %s, %s)
    """, (*processed_row[:-3], coordinates, processed_row[-2], processed_row[-1]))  # Все значения строки, кроме последних трех (координаты, комментарии и дата)

# Сохранение изменений
conn.commit()

# Проверка количества записей в таблице
cursor.execute("SELECT COUNT(*) FROM data_1")
count = cursor.fetchone()[0]
print(f"Количество записей в таблице data_1 после вставки всех строк: {count}")

# Закрытие соединения с базой данных
cursor.close()
conn.close()
