import os
import time
import pymysql
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# MySQL configuration from environment variables
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
MYSQL_DB = os.environ.get('MYSQL_DB', 'devops')


def get_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    """
    Retry DB connection because MySQL container
    may need time to become fully ready.
    """
    for i in range(30):   # Retry for ~60 seconds
        try:
            print(f"Trying MySQL connection... Attempt {i+1}")

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT
                )
            """)

            conn.commit()
            cur.close()
            conn.close()

            print("MySQL connected successfully.")
            return

        except Exception as e:
            print(f"MySQL not ready yet: {e}")
            time.sleep(2)

    raise Exception("Could not connect to MySQL after multiple retries.")


@app.route('/')
def home():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT message FROM messages")
    messages = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", messages=messages)


@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO messages (message) VALUES (%s)",
        (new_message,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": new_message})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)