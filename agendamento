import os
from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2 import sql
from psycopg2.errors import UniqueViolation

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    # Cria tabela
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            servico VARCHAR(100) NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL
        )
    """)

    # Adiciona constraint UNIQUE para evitar conflito real
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'unique_data_hora'
            ) THEN
                ALTER TABLE agendamentos
                ADD CONSTRAINT unique_data_hora UNIQUE (data, hora);
            END IF;
        END$$;
    """)

    conn.commit()
    cur.close()
    conn.close()

create_table()

@app.route("/")
def index():
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
        return "Horário já foi reservado por outra pessoa. Escolha outro."

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
    app.run(debug=True)
