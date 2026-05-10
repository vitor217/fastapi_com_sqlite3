from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI()


def conectar():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            status BOOLEAN DEFAULT FALSE
        )
    """)

    conn.commit()
    conn.close()


# cria a tabela ao iniciar
create_table()


@app.post("/tasks")
def post_task(nome: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (nome)
        VALUES (?)
    """, (nome,))

    conn.commit()

    task_id = cursor.lastrowid

    conn.close()

    return {
        "id": task_id,
        "nome": nome,
        "status": False
    }

@app.get("/tasks")
def get_tasks():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM tasks
""")
    tasks = cursor.fetchall()
    
    conn.close()
    
    return [dict(task) for task in tasks]

@app.put("/tasks/{id}")
def put_tasks(id:int, nome:str = None, status:bool = None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = cursor.fetchone()

    if not task:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    novo_nome = nome if nome is not None else task["nome"]
    novo_status = status if status is not None else task["status"]


    cursor.execute("""
    UPDATE tasks
    SET nome = ?, status = ?
    WHERE id = ?
    """, (novo_nome, novo_status, id,))

    conn.commit()
    
    conn.close()

    return {
        "id": id,
        "nome": novo_nome,
        "status": novo_status
    }

@app.delete("/tasks/{id}")
def delete_tasks(id:int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
DELETE FROM tasks WHERE id = ?
""", (id,))
    
    if not id:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    conn.commit()
    conn.close()
    return {"Tarefa":"Deletada"}
