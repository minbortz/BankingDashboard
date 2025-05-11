from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import pandas as pd
from typing import Optional
import os

app = Flask(__name__)

# MySQL configuration for AlwaysData
DB_USER = 'mahaka12'  
DB_PASS = 'mangolia_12345'  
DB_HOST = 'analog-hour-459515-f7:asia-southeast1:mahaka12' 
DB_NAME1 = 'database1'  
DB_NAME2 = 'database2'  

engine1 = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME1}')
engine2 = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME2}')

@app.route('/')
def index():
    return "API is running."

@app.route('/save_dataframe', methods=['POST'])
def save_dataframe():
    try:
        data = request.get_json()
        df = pd.DataFrame(data['data'])
        table_name = data['table_name']
        safe_table_name = table_name.lower().replace(" ", "_")
        df.to_sql(safe_table_name, con=engine1, if_exists='replace', index=False)
        return jsonify({"message": f"Data saved to `{safe_table_name}` successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search_database():
    try:
        query = request.json.get('query')
        with engine1.connect() as conn:
            result = conn.execute(text(query))
            if result.returns_rows:
                rows = [dict(row) for row in result.fetchall()]
                return jsonify(rows)
            else:
                return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/insert_user', methods=['POST'])
def insert_user():
    try:
        data = request.json
        query = text("""
            INSERT INTO user_information (userID, username, password, email, signup_time, role)
            VALUES (:userID, :username, :password, :email, :signup_time, :role)
        """)
        with engine2.connect() as conn:
            conn.execute(query, data)
            conn.commit()
        return jsonify({"message": "User inserted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/insert_admin', methods=['POST'])
def insert_admin():
    try:
        data = request.json
        query = text("""
            INSERT INTO admin_information (userID, username, password, email, signup_time, role)
            VALUES (:userID, :username, :password, :email, :signup_time, :role)
        """)
        with engine2.connect() as conn:
            conn.execute(query, data)
            conn.commit()
        return jsonify({"message": "Admin inserted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_user/<username>', methods=['GET'])
def get_user(username):
    try:
        query = text("SELECT * FROM user_information WHERE username = :username")
        with engine2.connect() as conn:
            result = conn.execute(query, {"username": username}).fetchone()
            if result:
                return jsonify(dict(result._mapping))
            else:
                return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_admin/<username>', methods=['GET'])
def get_admin(username):
    try:
        query = text("SELECT * FROM admin_information WHERE username = :username")
        with engine2.connect() as conn:
            result = conn.execute(query, {"username": username}).fetchone()
            if result:
                return jsonify(dict(result._mapping))
            else:
                return jsonify({"message": "Admin not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
