import mysql.connector
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def connect_mysql():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

def log_to_mysql(role, message, sources=None, user_id=None):
    if not user_id:
        user_id = "unknown"  # fallback

    if isinstance(sources, list):
        sources_str = ", ".join(str(s) for s in sources)
    else:
        sources_str = str(sources) if sources else None

    conn = connect_mysql()
    cursor = conn.cursor()

    sql = """
        INSERT INTO chat_logs (user_id, role, message, sources)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (user_id, role, message, sources_str))

    conn.commit()
    cursor.close()
    conn.close()



def get_chat_history(user_id):
    conn = connect_mysql()
    cursor = conn.cursor()

    sql = """
        SELECT role, message FROM chat_logs
        WHERE user_id = %s
        ORDER BY created_at ASC
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [{"role": role, "content": message} for role, message in rows]
