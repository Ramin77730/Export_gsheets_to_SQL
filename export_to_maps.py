import psycopg2
import json

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    host="localhost",  # Замените на ваш хост
    database="locations",  # Имя вашей базы данных
    user="postgres",  # Ваше имя пользователя
    password="75495"  # Ваш пароль
)
cursor = conn.cursor()

# Извлечение данных из таблицы
cursor.execute("SELECT point_name, ST_X(point_location::geometry), ST_Y(point_location::geometry) FROM marks")
data = cursor.fetchall()

# Форматирование данных в список словарей
locations = []
for row in data:
    locations.append({
        "name": row[0],
        "lat": row[2],
        "lng": row[1]
    })

# Сохранение данных в JSON-файл
with open('locations.json', 'w') as json_file:
    json.dump(locations, json_file)

# Закрытие соединения с базой данных
cursor.close()
conn.close()

print("Данные успешно экспортированы в locations.json!")
