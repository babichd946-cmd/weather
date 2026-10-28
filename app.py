from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import matplotlib

matplotlib.use('Agg')  #налаштування matplotlib для роботи без графічного інтерфейсу
import matplotlib.pyplot as plt

import weather_service
import database

app = Flask(__name__)

#ініціалізація бази даних при запуску застосунку
database.init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    """Головна сторінка. Пошук погоди за назвою міста та можливість збереження в БД"""
    weather_data = None
    error = None

    if request.method == 'POST':
        city_name = request.form.get('city_name')
        if not city_name:
            error = "Введіть назву міста для пошуку"
        else:
            #отримуємо дані через модуль weather_service
            result = weather_service.get_weather_by_city(city_name)
            if "error" in result:
                error = result["error"]
            else:
                weather_data = result
                #це якщо користувач натиснув кнопку збереження в базу
                if 'save_btn' in request.form:
                    database.save_weather_record(weather_data)
                    return redirect(url_for('saved_records'))

    return render_template('index.html', weather=weather_data, error=error)


@app.route('/compare', methods=['GET', 'POST'])
def compare_cities():
    """Завдання 5 та 7. Порівняння та генерація аналітичних графіків"""
    cities_data = []
    errors = []
    query = request.form.get('cities', 'Vienna, Bratislava, Prague')  #значення за замовчуванням для прикладу

    if request.method == 'POST':
        cities_data, errors = weather_service.get_multiple_cities_weather(query)

        #Генерація графіків за допомогою matplotlib, якщо є дані
        if cities_data:
            os.makedirs('static/images', exist_ok=True)

            city_names = [c['city_name'] for c in cities_data]
            temperatures = [c['temperature'] for c in cities_data]
            humidities = [c['humidity'] for c in cities_data]

            #Графік порівняння температур
            plt.figure(figsize=(7, 4))
            plt.bar(city_names, temperatures, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
            plt.xlabel('Міста')
            plt.ylabel('Температура (°C)')
            plt.title('Порівняння температур по локаціях')
            plt.tight_layout()
            chart_path_temp = 'static/images/temp_comparison.png'
            plt.savefig(chart_path_temp)
            plt.close()

            #Графік порівняння вологості
            plt.figure(figsize=(7, 4))
            plt.plot(city_names, humidities, marker='o', color='b', linewidth=2, markersize=8)
            plt.xlabel('Міста')
            plt.ylabel('Вологість (%)')
            plt.title('Порівняння рівня вологості')
            plt.grid(True)
            plt.tight_layout()
            chart_path_hum = 'static/images/humidity_comparison.png'
            plt.savefig(chart_path_hum)
            plt.close()

    return render_template('compare.html', cities=cities_data, errors=errors, query=query)


@app.route('/saved')
def saved_records():
    """Завдання 6 та 7. Сторінка збережених записів із локальним пошуком/фільтрацією"""
    query = request.args.get('q', '').strip()
    records = database.get_all_records()

    #Локальна фільтрація записів за назвою міста
    if query:
        records = [r for r in records if query.lower() in r['city_name'].lower()]

    return render_template('saved.html', records=records, query=query)


@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    """Редагування збереженого запису в локальній базі даних"""
    record = database.get_record_by_id(record_id)
    if not record:
        return "Запис не знайдено", 404

    if request.method == 'POST':
        new_city = request.form.get('city_name')
        if new_city:
            database.update_record(record_id, new_city)
            return redirect(url_for('saved_records'))

    return render_template('edit.html', record=record)


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    """Видалення запису з бази даних"""
    database.delete_record(record_id)
    return redirect(url_for('saved_records'))



#Завдання 8 - Таблиця 1. Власний REST API

@app.route('/api/items', methods=['GET'])
def api_get_items():
    """Отримати всі збережені записи у форматі JSON код 200"""
    records = database.get_all_records()
    items_list = [dict(row) for row in records]
    return jsonify(items_list), 200


@app.route('/api/items/<int:item_id>', methods=['GET'])
def api_get_item(item_id):
    """Отримати конкретний запис за ID код 200 або 404"""
    record = database.get_record_by_id(item_id)
    if not record:
        return jsonify({"error": "Ресурс не знайдено"}), 404
    return jsonify(dict(record)), 200


@app.route('/api/items', methods=['POST'])
def api_create_item():
    """Створити новий запис через REST API код 201 або 400"""
    data = request.get_json()
    if not data or 'city_name' not in data:
        return jsonify({"error": "Неправильні вхідні дані або відсутнє поле city_name"}), 400

    database.save_weather_record(data)
    return jsonify({"message": "Запис створено"}), 201


@app.route('/api/items/<int:item_id>', methods=['PATCH'])
def api_update_item(item_id):
    """Редагувати запис через REST API (код 200, 400 або 404)"""
    record = database.get_record_by_id(item_id)
    if not record:
        return jsonify({"error": "Ресурс не знайдено"}), 404

    data = request.get_json()
    new_name = data.get('city_name')
    if not new_name:
        return jsonify({"error": "Відсутнє обов'язкове поле city_name"}), 400

    database.update_record(item_id, new_name)
    return jsonify({"message": "Запис оновлено"}), 200


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def api_delete_item(item_id):
    """Видалити запис через REST API код 200 або 404"""
    record = database.get_record_by_id(item_id)
    if not record:
        return jsonify({"error": "Ресурс не знайдено"}), 404

    database.delete_record(item_id)
    return jsonify({"message": "Запис видалено"}), 200


if __name__ == '__main__':
    app.run(debug=True)