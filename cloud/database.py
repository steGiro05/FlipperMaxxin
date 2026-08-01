import sqlite3

DB="devices.db"


def get_db():

    return sqlite3.connect(DB)


def init_db():

    db=get_db()

    cursor=db.cursor()






    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        message TEXT,

        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)


    db.commit()
    db.close()

def add_log(message):

    db=get_db()

    db.execute(
        "INSERT INTO logs(message) VALUES(?)",
        (message,)
    )

    db.commit()
    db.close()
