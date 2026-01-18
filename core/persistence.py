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
        
        # Table for global permissions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_permissions (
                permission TEXT PRIMARY KEY,
                granted_at DATETIME
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
        
        # Table for Brain configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brains (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                privacy_level TEXT NOT NULL,
                config_json TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                is_fallback INTEGER DEFAULT 0,
                created_at DATETIME,
                last_health_check DATETIME,
                health_status TEXT,
                health_message TEXT
            )
        ''')
        
        # Table for Brain capabilities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_capabilities (
                brain_id TEXT,
                capability TEXT,
                FOREIGN KEY (brain_id) REFERENCES brains(id) ON DELETE CASCADE
            )
        ''')
        
        # Table for Brain usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brain_id TEXT,
                timestamp DATETIME,
                tokens_used INTEGER,
                cost_usd REAL,
                FOREIGN KEY (brain_id) REFERENCES brains(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_permission(self, permission):
        """Saves a globally granted permission to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO global_permissions (permission, granted_at)
                VALUES (?, ?)
            ''', (permission, datetime.datetime.now()))
            conn.commit()
        finally:
            conn.close()

    def revoke_permission(self, permission):
        """Removes a globally granted permission from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM global_permissions WHERE permission = ?
            ''', (permission,))
            conn.commit()
        finally:
            conn.close()

    def get_allowed_permissions(self):
        """Returns a list of all globally granted permissions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT permission FROM global_permissions')
        # Returns list of strings [perm1, perm2]
        perms = [row[0] for row in cursor.fetchall()]
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
    
    # ===== Brain Configuration Methods =====
    
    def save_brain_config(self, brain_id, name, provider, privacy_level, config_data, capabilities):
        """Save or update a Brain configuration."""
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Insert or replace Brain config
            cursor.execute('''
                INSERT OR REPLACE INTO brains 
                (id, name, provider, privacy_level, config_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (brain_id, name, provider, privacy_level, json.dumps(config_data), datetime.datetime.now()))
            
            # Delete old capabilities
            cursor.execute('DELETE FROM brain_capabilities WHERE brain_id = ?', (brain_id,))
            
            # Insert new capabilities
            for capability in capabilities:
                cursor.execute('''
                    INSERT INTO brain_capabilities (brain_id, capability)
                    VALUES (?, ?)
                ''', (brain_id, capability))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving Brain config: {e}")
            return False
        finally:
            conn.close()
    
    def load_brain_configs(self):
        """Load all Brain configurations."""
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM brains')
        rows = cursor.fetchall()
        
        brains = []
        for row in rows:
            brain_id, name, provider, privacy_level, config_json, is_active, is_fallback, created_at, last_health_check, health_status, health_message = row
            
            # Load capabilities
            cursor.execute('SELECT capability FROM brain_capabilities WHERE brain_id = ?', (brain_id,))
            capabilities = [cap[0] for cap in cursor.fetchall()]
            
            brains.append({
                'id': brain_id,
                'name': name,
                'provider': provider,
                'privacy_level': privacy_level,
                'config_data': json.loads(config_json),
                'is_active': bool(is_active),
                'is_fallback': bool(is_fallback),
                'capabilities': capabilities,
                'health_status': health_status,
                'health_message': health_message
            })
        
        conn.close()
        return brains
    
    def delete_brain_config(self, brain_id):
        """Delete a Brain configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM brains WHERE id = ?', (brain_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting Brain config: {e}")
            return False
        finally:
            conn.close()
    
    def set_active_brain(self, brain_id):
        """Set the active Brain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Clear all active flags
            cursor.execute('UPDATE brains SET is_active = 0')
            # Set new active
            cursor.execute('UPDATE brains SET is_active = 1 WHERE id = ?', (brain_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting active Brain: {e}")
            return False
        finally:
            conn.close()
    
    def set_fallback_brain(self, brain_id):
        """Set the fallback Brain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Clear all fallback flags
            cursor.execute('UPDATE brains SET is_fallback = 0')
            # Set new fallback
            cursor.execute('UPDATE brains SET is_fallback = 1 WHERE id = ?', (brain_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting fallback Brain: {e}")
            return False
        finally:
            conn.close()
    
    def update_brain_health(self, brain_id, status, message):
        """Update Brain health check status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE brains 
                SET last_health_check = ?, health_status = ?, health_message = ?
                WHERE id = ?
            ''', (datetime.datetime.now(), status, message, brain_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating Brain health: {e}")
            return False
        finally:
            conn.close()
    
    def log_brain_usage(self, brain_id, tokens_used, cost_usd):
        """Log Brain usage for tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO brain_usage (brain_id, timestamp, tokens_used, cost_usd)
                VALUES (?, ?, ?, ?)
            ''', (brain_id, datetime.datetime.now(), tokens_used, cost_usd))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error logging Brain usage: {e}")
            return False
        finally:
            conn.close()
    
    def get_brain_stats(self, brain_id, days=30):
        """Get usage statistics for a Brain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as request_count,
                SUM(tokens_used) as total_tokens,
                SUM(cost_usd) as total_cost
            FROM brain_usage
            WHERE brain_id = ? AND timestamp > ?
        ''', (brain_id, cutoff))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'request_count': row[0] or 0,
                'total_tokens': row[1] or 0,
                'total_cost': row[2] or 0.0
            }
        return {'request_count': 0, 'total_tokens': 0, 'total_cost': 0.0}

storage = Persistence()
