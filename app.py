from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Функция для загрузки данных из JSON-файла
def load_locations():
    with open(os.path.join(os.path.dirname(__file__), 'locations.json'), 'r', encoding='utf-8') as f:
        locations = json.load(f)
    return locations

# Маршрут для главной страницы
@app.route('/')
def index():
    locations = load_locations()
    return render_template("index.html", locations=locations)

# Маршрут для получения данных в формате JSON
@app.route('/api/locations')
def locations_api():
    locations = load_locations()
    return jsonify(locations)

# Маршрут для получения изображения
@app.route('/get_image/<file_id>')
def get_image(file_id):
    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(url)
    if response.status_code == 200:
        image = BytesIO(response.content)
        return send_file(image, mimetype='image/jpeg')
    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)
