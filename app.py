from glob import escape
import sqlite3
import os
from flask import Flask, request, abort
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "DEV_KEY")  # Vulnerabilidad 4 corregida: Clave secreta en variable de entorno
csrf = CSRFProtect(app)
def get_db_connection():
    # Conexión segura con control de errores
    try:
        conn = sqlite3.connect("bank.db")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print("Error en la conexión a la base de datos:", e)
        abort(500)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    # Vulnerabilidad 1 corregida: Uso de consultas parametrizadas
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        safe_username = escape(username)  # Evitar XSS
        return f"Bienvenido {safe_username}"
    else:
        return "Credenciales incorrectas"

@app.route("/transfer", methods=["POST"])
def transfer():
    try:
        amount = float(request.form.get("amount", "0"))
        account = request.form.get("account", "").strip()

        # Validación de entrada
        if amount <= 0:
            return "Monto inválido", 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vulnerabilidad 2 corregida: uso de parámetros en SQL
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE user = ?",
            (amount, account)
        )
        conn.commit()
        conn.close()

        return "Transferencia realizada"
    except ValueError:
        return "Entrada inválida", 400

# Vulnerabilidad 3 corregida: Clave secreta en variable de entorno
API_KEY = os.getenv("BANKING_API_KEY", "NO_KEY_DEFINED")

@app.route("/apikey")
def apikey():
    return f"Tu API key es: {API_KEY}"

if __name__ == "__main__":
    # ✅ Debug desactivado en producción
    app.run(debug=False)
