from flask import Flask, request, jsonify
import sqlite3
import os

class DatabaseManager:
    def __init__(self, database):
        self.database = database

    def get_connection(self):
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        return conn

    def table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (table_name,))
            return cursor.fetchone() is not None

    def create_table(self, table_name, columns):
        if self.table_exists(table_name):
            raise ValueError("Table already exists")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE {table_name} ({columns})")
            conn.commit()

    def insert_data(self, table_name, columns, values):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
            conn.commit()

    def fetch_all(self, table_name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()

class APIService:
    def __init__(self, app, db_manager):
        self.app = app
        self.db_manager = db_manager
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/create_table", methods=['POST'])
        def create_table():
            try:
                data = request.get_json()
                table_name = data['table_name']
                table_columns_names = data['table_columns_names']
                table_columns_types = data['table_columns_types']

                columns = ', '.join([f"{name} {col_type}" for name, col_type in zip(table_columns_names, table_columns_types)])
                self.db_manager.create_table(table_name, columns)

                return jsonify({"message": "Table created:)"}), 200

            except sqlite3.Error as e:
                print(f"SQLite error: {str(e)}")
                return jsonify({"error": str(e)}), 500

            except Exception as e:
                print(f"General error: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/write_query", methods=['POST'])
        def write_query():
            try:
                data = request.get_json()
                table_name = data['table_name']
                table_columns_names = ', '.join(data['table_columns_names'])
                values = ', '.join([
                    f"'{value}'" if isinstance(value, str) else str(int(value)) if isinstance(value, bool) else str(value)
                    for value in data['values']
                ])

                self.db_manager.insert_data(table_name, table_columns_names, values)

                return jsonify({"message": "Data inserted"}), 200

            except sqlite3.Error as e:
                print(f"SQLite error: {str(e)}")
                return jsonify({"error": str(e)}), 500

            except Exception as e:
                print(f"General error: {str(e)}")
                return jsonify({"error": str(e)}), 500

def create_app():
    app = Flask(__name__)
    db_manager = DatabaseManager('data.sql')
    APIService(app, db_manager)
    return app

if __name__ == '__main__':
    app = create_app()

    if not os.path.exists('data.sql'):
        with sqlite3.connect('data.sql') as conn:
            conn.commit()


    app.run(debug=True)