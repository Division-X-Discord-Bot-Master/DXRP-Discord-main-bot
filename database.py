import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='bot_database.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create all necessary tables"""
        # Warnings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bans table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Kicks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User data table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                guild_id INTEGER NOT NULL,
                username TEXT,
                join_date DATETIME,
                total_messages INTEGER DEFAULT 0,
                warnings_count INTEGER DEFAULT 0,
                last_seen DATETIME
            )
        ''')
        
        # Banned words table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS banned_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                added_by INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    # Warning methods
    def add_warning(self, user_id, guild_id, moderator_id, reason):
        """Add a warning to a user"""
        self.cursor.execute('''
            INSERT INTO warnings (user_id, guild_id, moderator_id, reason)
            VALUES (?, ?, ?, ?)
        ''', (user_id, guild_id, moderator_id, reason))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_warnings(self, user_id, guild_id):
        """Get all warnings for a user"""
        self.cursor.execute('''
            SELECT * FROM warnings 
            WHERE user_id = ? AND guild_id = ?
            ORDER BY timestamp DESC
        ''', (user_id, guild_id))
        return self.cursor.fetchall()
    
    def get_warning_count(self, user_id, guild_id):
        """Get warning count for a user"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM warnings 
            WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))
        return self.cursor.fetchone()[0]
    
    def clear_warnings(self, user_id, guild_id):
        """Clear all warnings for a user"""
        self.cursor.execute('''
            DELETE FROM warnings 
            WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))
        self.conn.commit()
    
    # Ban methods
    def add_ban(self, user_id, guild_id, moderator_id, reason):
        """Add a ban record"""
        self.cursor.execute('''
            INSERT INTO bans (user_id, guild_id, moderator_id, reason)
            VALUES (?, ?, ?, ?)
        ''', (user_id, guild_id, moderator_id, reason))
        self.conn.commit()
    
    def get_bans(self, user_id, guild_id):
        """Get all bans for a user"""
        self.cursor.execute('''
            SELECT * FROM bans 
            WHERE user_id = ? AND guild_id = ?
            ORDER BY timestamp DESC
        ''', (user_id, guild_id))
        return self.cursor.fetchall()
    
    # Kick methods
    def add_kick(self, user_id, guild_id, moderator_id, reason):
        """Add a kick record"""
        self.cursor.execute('''
            INSERT INTO kicks (user_id, guild_id, moderator_id, reason)
            VALUES (?, ?, ?, ?)
        ''', (user_id, guild_id, moderator_id, reason))
        self.conn.commit()
    
    # Security log methods
    def add_security_log(self, guild_id, user_id, action, details):
        """Add a security log entry"""
        self.cursor.execute('''
            INSERT INTO security_logs (guild_id, user_id, action, details)
            VALUES (?, ?, ?, ?)
        ''', (guild_id, user_id, action, details))
        self.conn.commit()
    
    def get_security_logs(self, guild_id, limit=50):
        """Get recent security logs"""
        self.cursor.execute('''
            SELECT * FROM security_logs 
            WHERE guild_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (guild_id, limit))
        return self.cursor.fetchall()
    
    # User methods
    def add_or_update_user(self, user_id, guild_id, username, join_date=None):
        """Add or update user data"""
        self.cursor.execute('''
            INSERT INTO users (user_id, guild_id, username, join_date, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                last_seen = excluded.last_seen
        ''', (user_id, guild_id, username, join_date or datetime.now(), datetime.now()))
        self.conn.commit()
    
    def increment_message_count(self, user_id):
        """Increment user's message count"""
        self.cursor.execute('''
            UPDATE users 
            SET total_messages = total_messages + 1,
                last_seen = ?
            WHERE user_id = ?
        ''', (datetime.now(), user_id))
        self.conn.commit()
    
    def get_user_stats(self, user_id, guild_id):
        """Get user statistics"""
        self.cursor.execute('''
            SELECT * FROM users WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))
        return self.cursor.fetchone()
    
    # Banned words methods
    def add_banned_word(self, word, added_by):
        """Add a banned word"""
        try:
            self.cursor.execute('''
                INSERT INTO banned_words (word, added_by)
                VALUES (?, ?)
            ''', (word.lower(), added_by))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_banned_word(self, word):
        """Remove a banned word"""
        self.cursor.execute('''
            DELETE FROM banned_words WHERE word = ?
        ''', (word.lower(),))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_banned_words(self):
        """Get all banned words"""
        self.cursor.execute('SELECT word FROM banned_words')
        return [row[0] for row in self.cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Create global database instance
db = Database()
