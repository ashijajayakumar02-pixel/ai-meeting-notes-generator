import sqlite3
from datetime import datetime

class ActionItem:
    def __init__(self, meeting_id, description, assignee, due_date, priority, id=None, completed=False):
        """Initialize Action Item object"""
        self.id = id
        self.meeting_id = meeting_id
        self.description = description
        self.assignee = assignee
        self.due_date = due_date
        self.priority = priority
        self.completed = completed
        self.created_at = datetime.now().isoformat() if not id else None

    @staticmethod
    def init_db():
        """Initialize database table"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                assignee TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'Medium',
                completed BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (meeting_id) REFERENCES meetings (id)
            )
        """)
        conn.commit()
        conn.close()

    def save(self):
        """Save action item to database"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()

        if self.id is None:
            # Insert new action item
            cursor.execute("""
                INSERT INTO action_items 
                (meeting_id, description, assignee, due_date, priority, completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.meeting_id, self.description, self.assignee, self.due_date, 
                  self.priority, self.completed, datetime.now().isoformat()))
            self.id = cursor.lastrowid
        else:
            # Update existing action item
            cursor.execute("""
                UPDATE action_items 
                SET description=?, assignee=?, due_date=?, priority=?, completed=?
                WHERE id=?
            """, (self.description, self.assignee, self.due_date, self.priority, 
                  self.completed, self.id))

        conn.commit()
        conn.close()
        return self.id

    @staticmethod
    def get_by_id(item_id):
        """Get action item by ID"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM action_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'meeting_id': row[1],
                'description': row[2],
                'assignee': row[3],
                'due_date': row[4],
                'priority': row[5],
                'completed': bool(row[6]),
                'created_at': row[7]
            }
        return None

    @staticmethod
    def get_by_meeting_id(meeting_id):
        """Get all action items for a meeting"""
        conn = sqlite3.connect('meetings.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM action_items 
            WHERE meeting_id = ? 
            ORDER BY priority DESC, created_at ASC
        """, (meeting_id,))
        rows = cursor.fetchall()
        conn.close()

        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'meeting_id': row[1],
                'description': row[2],
                'assignee': row[3],
                'due_date': row[4],
                'priority': row[5],
                'completed': bool(row[6]),
                'created_at': row[7]
            })
        return items