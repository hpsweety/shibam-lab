import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "shibam_coffee.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT
    )
    ''')

    # Samples table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_id TEXT UNIQUE NOT NULL,
        origin TEXT,
        farm TEXT,
        process TEXT,
        harvest_year TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Physical Assessments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS physical_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_id INTEGER,
        moisture REAL,
        defects_cat1 INTEGER,
        defects_cat2 INTEGER,
        screen_size TEXT,
        notes TEXT,
        assessed_by INTEGER,
        FOREIGN KEY (sample_id) REFERENCES samples (id),
        FOREIGN KEY (assessed_by) REFERENCES users (id)
    )
    ''')

    # Cupping Sessions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cupping_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roast_level TEXT,
        status TEXT DEFAULT 'Open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Session Samples (Link table with blind codes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS session_samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        sample_id INTEGER,
        blind_code TEXT,
        FOREIGN KEY (session_id) REFERENCES cupping_sessions (id),
        FOREIGN KEY (sample_id) REFERENCES samples (id)
    )
    ''')

    # Sensory Evaluations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensory_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_sample_id INTEGER,
        cupper_id INTEGER,
        fragrance REAL,
        flavor REAL,
        aftertaste REAL,
        acidity REAL,
        body REAL,
        sweetness REAL,
        balance REAL,
        clean_cup REAL,
        overall REAL,
        defect_flag INTEGER DEFAULT 0,
        notes TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_sample_id) REFERENCES session_samples (id),
        FOREIGN KEY (cupper_id) REFERENCES users (id)
    )
    ''')

    # Create default Admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                       ('admin', hashed, 'Admin', 'Default Administrator'))
        
        # Add some mock cuppers and roast managers for demo
        rm_hashed = bcrypt.hashpw("rm123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                       ('manager', rm_hashed, 'Roast Manager', 'Ahmad Roast Manager'))
        
        cupper_hashed = bcrypt.hashpw("cupper123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                       ('cupper1', cupper_hashed, 'Cupper', 'Sara Cupper'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
