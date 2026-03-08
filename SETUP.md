# Schnellstart-Anleitung

Diese Datei hilft, die API schnell in Betrieb zu nehmen.

## Schritt 1: Dateien prüfen

Sicherstellen dass folgende Daten verfügbar sind:

```
euer-projekt/
├── boxes_repository.py    ← Datenbank-Logik
├── box_server.py           ← REST API Server
├── test_boxes_api.py       ← Tests
├── requirements.txt        ← Python-Abhängigkeiten
├── README.md               ← Vollständige Dokumentation
└── SETUP.md                ← Diese Datei
```

## Schritt 2: Python-Pakete installieren

Terminal im Projektordner öffnen und folgendes ausführen:

```bash
pip install -r requirements.txt
```

**Was wird installiert?**
- `flask`: Das Web-Framework für die API
- `requests`: Für HTTP-Requests (brauchen die Tests)
- `pytest`: Test-Framework

## Schritt 3: Server starten

```bash
python box_server.py
```

Folgendes sollte sichtbar sein:

```
 * Running on http://0.0.0.0:5001
Press CTRL+C to quit
```

**Der Server läuft jetzt!** 

## Schritt 4: API testen

Öffnen eines **neuen Terminal-Tab** (Server muss weiterlaufen!) und folgendes testen:

### Test 1: Alle Kisten abrufen (noch leer)

```bash
curl http://localhost:5001/api/boxes
```

Antwort sollte sein:
```json
{
  "boxes": [],
  "total": 0,
  "_links": {...}
}
```

### Test 2: Erste Kiste erstellen

```bash
curl -X POST http://localhost:5001/api/boxes \
  -H "Content-Type: application/json" \
  -d '{"Location": "Küche", "Content": "Teller, Tassen"}'
```

Antwort:
```json
{
  "CODE": "AB12",  ← Euer CODE wird anders sein!
  "Location": "Küche",
  "Content": "Teller, Tassen",
  ...
}
```

### Test 3: Kiste abrufen

Ersetzt `AB12` mit eurem CODE:

```bash
curl http://localhost:5001/api/boxes/AB12
```

## Schritt 5: Tests ausführen

Im **zweiten Terminal** (Server läuft noch im ersten!):

```bash
pytest test_boxes_api.py -v
```

Folgendes sollte sichtbar sein:
```
========================= test session starts ==========================
test_boxes_api.py::TestCreateBox::test_create_box_with_all_data PASSED
test_boxes_api.py::TestCreateBox::test_create_box_without_location PASSED
...
========================= 25 passed in 2.45s ===========================
```



## Im Browser testen (optional)

Im Browser kann die API ebenfalls getestet werden:

1. Server starten: `python box_server.py`
2. Browser öffnen
3. URL eingeben: `http://localhost:5001/api/boxes`

Sichtbare JSON-Antwort direkt im Browser!

## Weitere Werkzeuge

### Postman (empfohlen für einfaches Testen)

1. Postman herunterladen: https://www.postman.com/downloads/
2. Erstellen einer neue Collection "Boxes API"
3. Requests hinzufügen:
   - GET `http://localhost:5001/api/boxes`
   - POST `http://localhost:5001/api/boxes`
   - usw.

### VS Code REST Client Extension

Bei verwendung von VS Code "REST Client" Extension installieren und eine Datei `requests.http` erstellen:

```http
### Get all boxes
GET http://localhost:5001/api/boxes

### Create box
POST http://localhost:5001/api/boxes
Content-Type: application/json

{
  "Location": "Küche",
  "Content": "Teller"
}
```

## Häufige Probleme

### "Port already in use" Fehler

Bei folgender Fehlermeldung:
```
OSError: [Errno 48] Address already in use
```

**Lösung**: Ein anderer Prozess nutzt Port 5001. Entweder:
1. Den anderen Prozess stoppen
2. Oder den Port in `box_server.py` ändern (Zeile ganz unten):
   ```python
   app.run(host='0.0.0.0', port=5001, debug=True)  # 5001 statt 5000
   ```

### "ModuleNotFoundError: No module named 'flask'"

**Lösung**: Pakete noch nicht installiert:
```bash
pip install -r requirements.txt
```

### Tests schlagen fehl mit "Connection refused"

**Lösung**: Der Server läuft nicht. In einem separaten Terminal starten:
```bash
python box_server.py
```

### Datenbank löschen/zurücksetzen

Zurücksetzen der Datenbank:
```bash
# Server stoppen (CTRL+C)
rm boxes.db
# Server neu starten
python box_server.py
```