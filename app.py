import sqlite3
from flask import Flask, request
app = Flask(__name__)
# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect("bank.db")
    return conn
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # ❌ Vulnerabilidad 1: Concatenación directa en consulta SQL (SQL Injection)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)  
    user = cursor.fetchone()
    if user:
        return f"Bienvenido {username}"
    else:
        return "Credenciales incorrectas"
@app.route("/transfer", methods=["POST"])
def transfer():
    amount = request.form["amount"]
    account = request.form["account"]
    # ❌ Vulnerabilidad 2: Falta de validación de entrada (input no controlado)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE accounts SET balance = balance - {amount} WHERE user = '{account}'")
    conn.commit()
    return "Transferencia realizada"
# ❌ Vulnerabilidad 3: Exposición de credenciales sensibles en el código
API_KEY = "12345-SECRET-HARDCODED-KEY"
@app.route("/apikey")
def apikey():
    return f"Tu API key es: {API_KEY}"
if __name__ == "__main__":
    app.run(debug=True)
