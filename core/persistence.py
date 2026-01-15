# MIT License - Copyright (c) 2026 Asigri Shamsu-Deen Al-Heyr
import sqlite3
import os
import datetime
from pathlib import Path

class Persistence:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "avva"
        self.db_path = self.config_dir / "avva.db"
        self._init_db()

    def _init_db(self):
        """Creates the database and tables if they don't exist."""
        os.makedirs(self.config_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for persistent permissions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT,
                permission TEXT,
                granted_at DATETIME,
                UNIQUE(skill_name, permission)
            )
        ''')
        
        # Table for interaction history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                sender TEXT,
                message TEXT,
                tool_call TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_permission(self, skill_name, permission):
        """Saves a granted permission to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO permissions (skill_name, permission, granted_at)
                VALUES (?, ?, ?)
            ''', (skill_name, permission, datetime.datetime.now()))
            conn.commit()
        finally:
            conn.close()

    def get_allowed_permissions(self):
        """Returns a list of all granted (skill, permission) tuples."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT skill_name, permission FROM permissions')
        perms = cursor.fetchall()
        conn.close()
        return perms

    def log_interaction(self, sender, message, tool_call=None):
        """Logs an interaction to the history table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO history (timestamp, sender, message, tool_call)
                VALUES (?, ?, ?, ?)
            ''', (datetime.datetime.now(), sender, message, tool_call))
            conn.commit()
        finally:
            conn.close()

storage = Persistence()
