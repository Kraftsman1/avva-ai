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

        # Table for conversation sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                created_at DATETIME,
                updated_at DATETIME,
                title TEXT,
                brain_id TEXT,
                pinned INTEGER DEFAULT 0
            )
        ''')

        # Table for conversation messages (richer than history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME,
                brain_id TEXT,
                intent TEXT,
                tool_call TEXT,
                embedding TEXT,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions(id) ON DELETE CASCADE
            )
        ''')

        # Table for memory/recalls (for semantic search)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT,
                source TEXT,
                created_at DATETIME,
                expires_at DATETIME,
                embedding TEXT
            )
        ''')

        # Table for settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME
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

    # ===== Conversation Memory Methods =====

    def create_session(self, session_id=None, title=None, brain_id=None):
        """Create a new conversation session."""
        import uuid
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            session_id = session_id or str(uuid.uuid4())
            now = datetime.datetime.now()
            cursor.execute('''
                INSERT INTO conversation_sessions (id, created_at, updated_at, title, brain_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, now, now, title or "New Conversation", brain_id))
            conn.commit()
            return session_id
        finally:
            conn.close()

    def add_message(self, session_id, role, content, brain_id=None, intent=None, tool_call=None):
        """Add a message to a conversation session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            now = datetime.datetime.now()
            cursor.execute('''
                INSERT INTO conversation_messages (session_id, role, content, timestamp, brain_id, intent, tool_call)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, role, content, now, brain_id, intent, tool_call))
            cursor.execute('''
                UPDATE conversation_sessions SET updated_at = ? WHERE id = ?
            ''', (now, session_id))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_session(self, session_id):
        """Get a conversation session by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, created_at, updated_at, title, brain_id, pinned
                FROM conversation_sessions WHERE id = ?
            ''', (session_id,))
            row = cursor.fetchone()
            if row:
                from datetime import datetime
                return {
                    'id': row[0],
                    'created_at': datetime.fromisoformat(row[1]) if row[1] else None,
                    'updated_at': datetime.fromisoformat(row[2]) if row[2] else None,
                    'title': row[3],
                    'brain_id': row[4],
                    'pinned': bool(row[5]) if len(row) > 5 else False
                }
            return None
        finally:
            conn.close()

    def get_session_messages(self, session_id, limit=100):
        """Get all messages in a conversation session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, role, content, timestamp, brain_id, intent, tool_call
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (session_id, limit))
            rows = cursor.fetchall()
            from datetime import datetime
            return [{
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'timestamp': datetime.fromisoformat(row[3]) if row[3] else None,
                'brain_id': row[4],
                'intent': row[5],
                'tool_call': row[6]
            } for row in rows]
        finally:
            conn.close()

    def list_sessions(self, limit=50, offset=0):
        """List recent conversation sessions, pinned first."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, created_at, updated_at, title, brain_id, COALESCE(pinned, 0) as pinned
                FROM conversation_sessions
                ORDER BY pinned DESC, updated_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            from datetime import datetime
            return [{
                'id': row[0],
                'created_at': datetime.fromisoformat(row[1]) if row[1] else None,
                'updated_at': datetime.fromisoformat(row[2]) if row[2] else None,
                'title': row[3],
                'brain_id': row[4],
                'pinned': bool(row[5])
            } for row in rows]
        finally:
            conn.close()

    def search_conversations(self, query, limit=10):
        """Search conversations by content (simple LIKE search)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            search_term = f"%{query}%"
            cursor.execute('''
                SELECT DISTINCT m.session_id, s.title, s.updated_at
                FROM conversation_messages m
                JOIN conversation_sessions s ON m.session_id = s.id
                WHERE m.content LIKE ?
                ORDER BY s.updated_at DESC
                LIMIT ?
            ''', (search_term, limit))
            rows = cursor.fetchall()
            from datetime import datetime
            return [{
                'session_id': row[0],
                'title': row[1],
                'updated_at': datetime.fromisoformat(row[2]) if row[2] else None
            } for row in rows]
        finally:
            conn.close()

    def update_session_title(self, session_id, title):
        """Update a session's title."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            now = datetime.datetime.now()
            cursor.execute('''
                UPDATE conversation_sessions
                SET title = ?, updated_at = ?
                WHERE id = ?
            ''', (title, now, session_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating session title: {e}")
            return False
        finally:
            conn.close()

    def toggle_session_pin(self, session_id):
        """Toggle pin status for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Get current pin status
            cursor.execute('SELECT COALESCE(pinned, 0) FROM conversation_sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            if row:
                current_pinned = bool(row[0])
                new_pinned = 0 if current_pinned else 1
                cursor.execute('''
                    UPDATE conversation_sessions
                    SET pinned = ?
                    WHERE id = ?
                ''', (new_pinned, session_id))
                conn.commit()
                return bool(new_pinned)
            return False
        except Exception as e:
            print(f"Error toggling session pin: {e}")
            return False
        finally:
            conn.close()

    def delete_session(self, session_id):
        """Delete a conversation session and all its messages."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM conversation_messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM conversation_sessions WHERE id = ?', (session_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
        finally:
            conn.close()

    def delete_old_sessions(self, days=30):
        """Delete sessions older than specified days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
            cursor.execute('''
                DELETE FROM conversation_messages
                WHERE session_id IN (
                    SELECT id FROM conversation_sessions WHERE updated_at < ?
                )
            ''', (cutoff,))
            cursor.execute('DELETE FROM conversation_sessions WHERE updated_at < ?', (cutoff,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting old sessions: {e}")
            return False
        finally:
            conn.close()

    # ===== Settings Methods =====

    def get_setting(self, key, default=None):
        """Get a setting value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else default
        finally:
            conn.close()

    def set_setting(self, key, value):
        """Set a setting value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            now = datetime.datetime.now()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, now))
            conn.commit()
            return True
        finally:
            conn.close()

storage = Persistence()
