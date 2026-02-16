import os
from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2.errors import UniqueViolation

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada no Render.")
    
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            servico VARCHAR(100) NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL,
            UNIQUE (data, hora)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():
    create_table()  # garante que a tabela existe

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agendamentos ORDER BY data, hora")
    agendamentos = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", agendamentos=agendamentos)


@app.route("/agendar", methods=["POST"])
def agendar():
    nome = request.form["nome"]
    servico = request.form["servico"]
    data = request.form["data"]
    hora = request.form["hora"]

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO agendamentos (nome, servico, data, hora)
            VALUES (%s, %s, %s, %s)
        """, (nome, servico, data, hora))

        conn.commit()

    except UniqueViolation:
        conn.rollback()
        cur.close()
        conn.close()
        return "Horário já foi reservado por outra pessoa."

    cur.close()
    conn.close()

    return redirect("/")


@app.route("/cancelar/<int:id>")
def cancelar(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM agendamentos WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
