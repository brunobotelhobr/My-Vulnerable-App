"""
Arquivo de funções vulneráveis para testes de CodeQL.
Cada função abaixo contém vulnerabilidades reais que podem ser detectadas por CodeQL,
como SQL Injection, XSS, uso inseguro de subprocessos, etc.
"""

import sqlite3
import subprocess
from flask import request, escape


def vulnerable_sql_injection(user_input) -> list[Any]:
    # Vulnerabilidade: SQL Injection
    conn = sqlite3.connect(database="app.db")
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    c.execute(query)  # CodeQL detecta uso inseguro de input
    return c.fetchall()


def vulnerable_xss() -> str:
    # Vulnerabilidade: XSS Refletido
    name: str = request.args.get(key="name", default="")
    return f"<h1>Hello {name}</h1>"  # CodeQL detecta uso inseguro de input em HTML


def vulnerable_subprocess(cmd) -> None:
    # Vulnerabilidade: Command Injection
    subprocess.call(cmd, shell=True)  # CodeQL detecta uso inseguro de shell=True


# Função "inofensiva" para comparação
def safe_sql(user_input) -> list[Any]:
    conn: sqlite3.Connection = sqlite3.connect(database="app.db")
    c: sqlite3.Cursor = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", parameters=(user_input,))
    return c.fetchall()
