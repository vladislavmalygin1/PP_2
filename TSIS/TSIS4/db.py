import psycopg2
from datetime import datetime

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def init_db():
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_user(username):
    conn = get_connection()
    if not conn: return None
    cur = conn.cursor()
    cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING", (username,))
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    uid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return uid

def save_game(user_id, score, level):
    if user_id is None: return
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    # This automatically saves the score to the history
    cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)", 
                (user_id, score, level))
    conn.commit()
    cur.close()
    conn.close()

def get_leaderboard():
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            p.username, 
            MAX(g.score) as best, 
            MAX(g.level_reached), 
            MAX(g.played_at)::date 
        FROM game_sessions g 
        JOIN players p ON g.player_id = p.id 
        GROUP BY p.username 
        ORDER BY best DESC 
        LIMIT 10
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_personal_best(user_id):
    conn = get_connection()
    if not conn: return (0, 1)
    cur = conn.cursor()
    cur.execute("SELECT score, level_reached FROM game_sessions WHERE player_id = %s ORDER BY score DESC LIMIT 1", (user_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res if res else (0, 1)



