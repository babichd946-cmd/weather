import sqlite3

DB_NAME = 'weather.db'


def get_db_connection():
    """Створює підключення до бази даних SQLite"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Створює таблицю weather_records з необхідними полями та обмеженнями цілісності"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name VARCHAR(100) NOT NULL,
            temperature FLOAT,
            humidity INTEGER,
            wind_speed FLOAT,
            condition VARCHAR(100),
            external_id INTEGER,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def save_weather_record(data):
    """Зберігає запис про погоду в базу даних за допомогою параметризованого запиту, тобто реалізує захист від SQL-ін'єкцій"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO weather_records (city_name, temperature, humidity, wind_speed, condition, external_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('city_name'),
        data.get('temperature'),
        data.get('humidity'),
        data.get('wind_speed'),
        data.get('condition'),
        data.get('external_id')
    ))

    conn.commit()
    conn.close()


def get_all_records():
    """Отримує всі збережені записи з локальної бази даних"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM weather_records ORDER BY recorded_at DESC')
    records = cursor.fetchall()
    conn.close()
    return records


def get_record_by_id(record_id):
    """Отримує конкретний запис за його ідентифікатором"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM weather_records WHERE id = ?', (record_id,))
    record = cursor.fetchone()
    conn.close()
    return record


def update_record(record_id, city_name):
    """Редагує збережений запис"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE weather_records 
        SET city_name = ? 
        WHERE id = ?
    ''', (city_name, record_id))
    conn.commit()
    conn.close()


def delete_record(record_id):
    """Видаляє запис із бази даних за ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM weather_records WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Ініціалізація бази даних та CRUD-функцій виконана")