import sqlite3
import json
from datetime import datetime

class Meeting:
    def __init__(self, title, date, attendees, transcription, summary, id=None):
        """Initialize Meeting object"""
        self.id = id
        self.title = title
        self.date = date
        self.attendees = attendees
        self.transcription = transcription
        self.summary = summary
        self.created_at = datetime.now().isoformat() if not id else None

    @staticmethod
    def init_db():
        """Initialize database table"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                attendees TEXT,
                transcription TEXT NOT NULL,
                summary TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save(self):
        """Save meeting to database"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()

        if self.id is None:
            # Insert new meeting
            cursor.execute("""
                INSERT INTO meetings (title, date, attendees, transcription, summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.title, self.date, self.attendees, self.transcription, 
                  self.summary, datetime.now().isoformat()))
            self.id = cursor.lastrowid
        else:
            # Update existing meeting
            cursor.execute("""
                UPDATE meetings 
                SET title=?, date=?, attendees=?, transcription=?, summary=?
                WHERE id=?
            """, (self.title, self.date, self.attendees, self.transcription, 
                  self.summary, self.id))

        conn.commit()
        conn.close()
        return self.id

    @staticmethod
    def get_by_id(meeting_id):
        """Get meeting by ID"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM meetings WHERE id = ?', (meeting_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'title': row[1],
                'date': row[2],
                'attendees': row[3],
                'transcription': row[4],
                'summary': row[5],
                'created_at': row[6]
            }
        return None

    @staticmethod
    def get_all():
        """Get all meetings"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM meetings ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        meetings = []
        for row in rows:
            meetings.append({
                'id': row[0],
                'title': row[1],
                'date': row[2],
                'attendees': row[3],
                'transcription': row[4],
                'summary': row[5],
                'created_at': row[6]
            })
        return meetings