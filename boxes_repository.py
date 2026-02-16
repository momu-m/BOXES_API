"""
Repository für Kisten-Verwaltung
Verwaltet alle Datenbank-Operationen für Kisten
"""
import sqlite3
import random
import string
from datetime import datetime


class BoxesRepository:
    def __init__(self, db_name='boxes.db'):
        """Initialisiert das Repository und erstellt die Datenbank"""
        self.db_name = db_name
        self._init_database()
    
    def _init_database(self):
        """Erstellt die Datenbank-Tabelle, falls sie nicht existiert"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boxes (
                CODE TEXT PRIMARY KEY NOT NULL,
                Location TEXT,
                Content TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Erstellt eine neue Datenbankverbindung"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Ermöglicht dict-ähnlichen Zugriff
        return conn
    
    def generate_unique_code(self):
        """
        Generiert einen eindeutigen Code für eine neue Kiste
        Format: 2 Großbuchstaben + 2 Zahlen (z.B. AB12)
        """
        while True:
            # Generiere Code: 2 Buchstaben + 2 Zahlen
            code = ''.join(random.choices(string.ascii_uppercase, k=2))
            code += ''.join(random.choices(string.digits, k=2))
            
            # Prüfe ob Code schon existiert
            if not self.get(code):
                return code
    
    def create(self, code=None, location='', content=''):
        """
        Erstellt eine neue Kiste
        
        Args:
            code: Optional - CODE der Kiste (wird generiert wenn nicht angegeben)
            location: Optional - Standort der Kiste
            content: Optional - Inhalt der Kiste
        
        Returns:
            dict: Die erstellte Kiste oder None bei Fehler
        """
        if not code:
            code = self.generate_unique_code()
        
        now = datetime.now().isoformat()
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO boxes (CODE, Location, Content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                (code, location, content, now, now)
            )
            conn.commit()
            
            # Hole die neu erstellte Kiste
            new_box = self.get(code)
            conn.close()
            return new_box
        except sqlite3.IntegrityError:
            return None  # CODE existiert bereits
    
    def get_all(self):
        """
        Holt alle Kisten aus der Datenbank
        
        Returns:
            list: Liste aller Kisten als Dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM boxes ORDER BY CODE')
        boxes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return boxes
    
    def get(self, code):
        """
        Holt eine spezifische Kiste anhand ihres CODEs
        
        Args:
            code: CODE der gesuchten Kiste
        
        Returns:
            dict: Die Kiste oder None wenn nicht gefunden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM boxes WHERE CODE = ?', (code,))
        box = cursor.fetchone()
        conn.close()
        
        if box:
            return dict(box)
        return None
    
    def update(self, code, location=None, content=None):
        """
        Aktualisiert eine Kiste
        
        Args:
            code: CODE der zu aktualisierenden Kiste
            location: Neuer Standort (optional)
            content: Neuer Inhalt (optional)
        
        Returns:
            dict: Die aktualisierte Kiste oder None wenn nicht gefunden
        """
        # Hole aktuelle Kiste
        current_box = self.get(code)
        if not current_box:
            return None
        
        # Nutze alte Werte wenn keine neuen angegeben
        new_location = location if location is not None else current_box['Location']
        new_content = content if content is not None else current_box['Content']
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE boxes SET Location = ?, Content = ?, updated_at = ? WHERE CODE = ?',
            (new_location, new_content, now, code)
        )
        conn.commit()
        conn.close()
        
        return self.get(code)
    
    def delete(self, code):
        """
        Löscht eine Kiste
        
        Args:
            code: CODE der zu löschenden Kiste
        
        Returns:
            bool: True wenn erfolgreich gelöscht, False wenn nicht gefunden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM boxes WHERE CODE = ?', (code,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_all_locations(self):
        """
        Holt eine Liste aller eindeutigen Standorte
        
        Returns:
            list: Liste aller Standorte (ohne Duplikate)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT Location FROM boxes WHERE Location IS NOT NULL AND Location != ""')
        locations = [row['Location'] for row in cursor.fetchall()]
        conn.close()
        return locations
    
    def count_boxes(self):
        """
        Zählt die Gesamtanzahl der Kisten
        
        Returns:
            int: Anzahl der Kisten
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM boxes')
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def count_locations(self):
        """
        Zählt die Anzahl unterschiedlicher Standorte
        
        Returns:
            int: Anzahl der Standorte
        """
        return len(self.get_all_locations())
