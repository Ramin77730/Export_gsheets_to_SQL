import psycopg2
import json
from decimal import Decimal
from datetime import date


# Функция для преобразования типов данных в JSON-совместимые форматы
def convert_to_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, date):
        return obj.isoformat()  # Преобразуем дату в строку в формате ISO (YYYY-MM-DD)
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")


# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    host="localhost",  # Хост базы данных
    database="locations",  # Имя базы данных
    user="postgres",  # Имя пользователя базы данных
    password="75495"  # Пароль пользователя
)
cursor = conn.cursor()

# Извлечение данных из таблицы, включая все необходимые поля
cursor.execute("""
    SELECT 
        name,
        voltage,
        length_1,
        length_2,
        length_3,
        length_4,
        length_5,
        width_1,
        width_2,
        width_3,
        ST_X(coordinates::geometry) AS lng, 
        ST_Y(coordinates::geometry) AS lat,
        photo_1, 
        photo_2, 
        photo_3, 
        photo_4, 
        photo_5,
        comments,
        date
    FROM data_1
""")
data = cursor.fetchall()

# Форматирование данных в список словарей
locations = []
for row in data:
    photos = [photo for photo in row[12:17] if photo]  # Фильтруем пустые ссылки на фото

    locations.append({
        "name": row[0],  # Название локации
        "voltage": row[1],  # Напряжение
        "lengths": {  # Длины
            "length_1": row[2],
            "length_2": row[3],
            "length_3": row[4],
            "length_4": row[5],
            "length_5": row[6],
        },
        "widths": {  # Ширины
            "width_1": row[7],
            "width_2": row[8],
            "width_3": row[9],
        },
        "lng": row[10],  # Долгота
        "lat": row[11],  # Широта
        "photos": photos,  # Ссылки на фото
        "comments": row[17],  # Комментарии
        "date": row[18]  # Дата
    })

# Сохранение данных в JSON-файл с использованием custom encoder
with open('locations.json', 'w', encoding='utf-8') as json_file:
    json.dump(locations, json_file, ensure_ascii=False, indent=4, default=convert_to_serializable)

# Закрытие соединения с базой данных
cursor.close()
conn.close()

print("Данные успешно экспортированы в locations.json!")
