import os
from flask import Flask, render_template, request, redirect, session
import psycopg2
from psycopg2.errors import UniqueViolation

app = Flask(__name__)
app.secret_key = "segredo"

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            servico VARCHAR(100),
            data DATE,
            hora TIME,
            UNIQUE (data, hora)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

create_table()

# CLIENTE
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/agendar", methods=["POST"])
def agendar():
    nome = request.form["nome"]
    servico = request.form["servico"]
    data = request.form["data"]
    hora = request.form["hora"]

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO agendamentos (nome, servico, data, hora) VALUES (%s,%s,%s,%s)",
            (nome, servico, data, hora),
        )
        conn.commit()
    except UniqueViolation:
        conn.rollback()
        return "Horário ocupado"

    cur.close()
    conn.close()

    return redirect("/")

# LOGIN ADMIN
@app.route("/admin")
def admin():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    user = request.form["usuario"]
    senha = request.form["senha"]

    if user == "admin" and senha == "1234":
        session["admin"] = True
        return redirect("/painel")

    return "Login inválido"

@app.route("/painel")
def painel():
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agendamentos ORDER BY data, hora")
    dados = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("painel.html", dados=dados)

@app.route("/cancelar/<int:id>")
def cancelar(id):
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM agendamentos WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/painel")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
