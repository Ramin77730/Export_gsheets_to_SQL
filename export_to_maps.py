import psycopg2
import json
import os
from decimal import Decimal

# Параметры подключения к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="locations",
    user="postgres",
    password="75495"
)
cursor = conn.cursor()

# SQL-запрос для извлечения данных из таблицы
cursor.execute("""
    SELECT id, name, voltage, length_1, length_2, length_3, length_4, length_5,
           width_1, width_2, width_3, photo_1, photo_2, photo_3, photo_4, photo_5,
           ST_X(coordinates) as lng, ST_Y(coordinates) as lat, comments, date
    FROM data_1
""")
rows = cursor.fetchall()

# Функция для преобразования объекта Decimal в float или строку
def convert_decimal(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

# Преобразование данных в формат JSON
data = []
for row in rows:
    record = {
        "id": row[0],
        "name": row[1],
        "voltage": row[2],
        "length_1": convert_decimal(row[3]),
        "length_2": convert_decimal(row[4]),
        "length_3": convert_decimal(row[5]),
        "length_4": convert_decimal(row[6]),
        "length_5": convert_decimal(row[7]),
        "width_1": convert_decimal(row[8]),
        "width_2": convert_decimal(row[9]),
        "width_3": convert_decimal(row[10]),
        "photos": [
            row[11],  # photo_1
            row[12],  # photo_2
            row[13],  # photo_3
            row[14],  # photo_4
            row[15]   # photo_5
        ],
        "coordinates": {
            "lat": convert_decimal(row[17]),
            "lng": convert_decimal(row[16])
        },
        "comments": row[18],
        "date": row[19].isoformat() if row[19] else None  # Преобразование даты в формат ISO
    }
    data.append(record)

# Путь к JSON-файлу
json_file_path = os.path.join(os.path.dirname(__file__), 'data.json')

# Сохранение данных в JSON-файл
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

# Закрытие соединения с базой данных
cursor.close()
conn.close()

print(f"Данные успешно сохранены в {json_file_path}")
