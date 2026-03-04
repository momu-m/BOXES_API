# Kisten-Verwaltungs REST-API

Eine vollständige REST-API zur Verwaltung von Kisten mit Standort und Inhalt.
Erstellt duch Mo, Arjen und Andrin.

## Projektübersicht

Diese API ermöglicht die Verwaltung von Kisten durch:
- **Erstellen** neuer Kisten mit automatisch generierten Codes
- **Auslesen** aller Kisten oder einzelner Kisten
- **Aktualisieren** von Standort und Inhalt
- **Löschen** von Kisten
- **Statistiken** über Anzahl und Standorte

## Inhaltsverzeichnis

- [Installation und Start](#installation-und-start)
- [API-Dokumentation](#api-dokumentation)
- [REST-Prinzipien](#rest-prinzipien)
- [Tests ausführen](#tests-ausführen)
- [Datenbank-Struktur](#datenbank-struktur)
- [Beispiele](#beispiele)

---

## Installation und Start

### Voraussetzungen

- Python 3.10 oder höher
- pip (Python Package Manager)

### Schritt 1: Abhängigkeiten installieren

```bash
pip install flask requests pytest
```

### Schritt 2: Server starten

```bash
python box_server.py
```

Der Server läuft nun auf: `http://localhost:5001`

### Schritt 3: API testen

In einem neuen Terminal:

```bash
# Alle Kisten abrufen
curl http://localhost:5001/api/boxes

# Neue Kiste erstellen
curl -X POST http://localhost:5001/api/boxes \
  -H "Content-Type: application/json" \
  -d '{"Location": "Küche", "Content": "Teller, Tassen"}'
```

---

## Swagger UI (Interaktive Dokumentation)

Nach dem Starten des Servers ist die interaktive Swagger UI erreichbar unter:

```
http://localhost:5001/apidocs
```

Dort kann man alle Endpunkte direkt im Browser testen, ohne Curl oder Postman zu brauchen.

---

## API-Dokumentation

### Basis-URL

```
http://localhost:5001/api/boxes
```

### Endpunkte

#### 1. Alle Kisten abrufen

```http
GET /api/boxes
```

**Response (200 OK):**
```json
{
  "boxes": [
    {
      "CODE": "AB12",
      "Location": "Küche",
      "Content": "Teller, Tassen",
      "created_at": "2026-02-16T10:30:00",
      "updated_at": "2026-02-16T10:30:00",
      "_links": {
        "self": {"href": "/api/boxes/AB12", "method": "GET"},
        "update": {"href": "/api/boxes/AB12", "method": "PUT"},
        "delete": {"href": "/api/boxes/AB12", "method": "DELETE"}
      }
    }
  ],
  "total": 1,
  "_links": {
    "self": {"href": "/api/boxes", "method": "GET"},
    "create": {"href": "/api/boxes", "method": "POST"}
  }
}
```

**Cache-Header:**
- `ETag`: Eindeutiger Hash der Daten
- `Cache-Control`: `max-age=60, must-revalidate`

---

#### 2. Einzelne Kiste abrufen

```http
GET /api/boxes/{CODE}
```

**Parameter:**
- `CODE`: Der eindeutige Code der Kiste (z.B. "AB12")

**Response (200 OK):**
```json
{
  "CODE": "AB12",
  "Location": "Küche",
  "Content": "Teller, Tassen",
  "created_at": "2026-02-16T10:30:00",
  "updated_at": "2026-02-16T10:30:00",
  "_links": {
    "self": {"href": "/api/boxes/AB12", "method": "GET"},
    "update": {"href": "/api/boxes/AB12", "method": "PUT"},
    "delete": {"href": "/api/boxes/AB12", "method": "DELETE"},
    "collection": {"href": "/api/boxes", "method": "GET"}
  }
}
```

**Fehler (404 Not Found):**
```json
{
  "error": "Nicht gefunden",
  "message": "Kiste mit CODE AB12 existiert nicht"
}
```

---

#### 3. Neue Kiste erstellen

```http
POST /api/boxes
```

**Request Body (JSON):**
```json
{
  "Location": "Küche",
  "Content": "Teller, Tassen"
}
```

**Optionale Felder:**
- `CODE`: Eigener Code (wird sonst automatisch generiert)
- `Location`: Standort (optional)
- `Content`: Inhalt (optional)

**Response (201 Created):**
```json
{
  "CODE": "AB12",
  "Location": "Küche",
  "Content": "Teller, Tassen",
  "created_at": "2026-02-16T10:30:00",
  "updated_at": "2026-02-16T10:30:00",
  "_links": {
    "self": {"href": "/api/boxes/AB12", "method": "GET"},
    "update": {"href": "/api/boxes/AB12", "method": "PUT"},
    "delete": {"href": "/api/boxes/AB12", "method": "DELETE"}
  }
}
```

**Header:**
- `Location`: `/api/boxes/AB12` (URL der neu erstellten Ressource)

---

#### 4. Kiste aktualisieren

```http
PUT /api/boxes/{CODE}
```

**Request Body (JSON):**
```json
{
  "Location": "Keller",
  "Content": "Werkzeug, Schrauben"
}
```

**Response (200 OK):**
```json
{
  "CODE": "AB12",
  "Location": "Keller",
  "Content": "Werkzeug, Schrauben",
  "created_at": "2026-02-16T10:30:00",
  "updated_at": "2026-02-16T11:15:00",
  "_links": {...}
}
```

---

#### 5. Kiste löschen

```http
DELETE /api/boxes/{CODE}
```

**Response (204 No Content):**
- Kein Body
- Status Code 204 = erfolgreich gelöscht

**Fehler (404 Not Found):**
```json
{
  "error": "Nicht gefunden",
  "message": "Kiste mit CODE AB12 existiert nicht"
}
```

---

#### 6. Alle Standorte abrufen

```http
GET /api/boxes/locations
```

**Response (200 OK):**
```json
{
  "locations": ["Küche", "Keller", "Garage"],
  "total": 3,
  "_links": {
    "self": {"href": "/api/boxes/locations", "method": "GET"},
    "collection": {"href": "/api/boxes", "method": "GET"}
  }
}
```

---

#### 7. Statistiken abrufen

```http
GET /api/boxes/stats
```

**Response (200 OK):**
```json
{
  "total_boxes": 15,
  "total_locations": 5,
  "_links": {
    "self": {"href": "/api/boxes/stats", "method": "GET"},
    "collection": {"href": "/api/boxes", "method": "GET"},
    "locations": {"href": "/api/boxes/locations", "method": "GET"}
  }
}
```

---

## REST-Prinzipien

Diese API implementiert alle geforderten REST-Prinzipien vollständig:

### 1. Zustandslosigkeit

**Implementierung:**
- Server speichert **keine** Session-Daten zwischen Requests
- Jeder Request enthält alle notwendigen Informationen
- Keine serverseitigen Cookies oder Sessions

**Beispiel:**
```python
# Jeder Request ist unabhängig
GET /api/boxes/AB12  # Request 1
GET /api/boxes/AB12  # Request 2 - Server "erinnert" sich nicht an Request 1
```

---

### 2. Caching 

**Implementierung:**
- **ETag Header**: Eindeutiger Hash-Wert der Daten für Versionierung
- **Cache-Control Header**: `max-age=60, must-revalidate` (Daten 60 Sekunden gültig)
- **Last-Modified Header**: Zeitstempel der letzten Änderung
- **304 Not Modified**: Wenn Client bereits aktuelle Daten hat

**Code-Beispiel:**
```python
def add_cache_headers(response, etag, max_age=60):
    response.headers['ETag'] = f'"{etag}"'
    response.headers['Cache-Control'] = f'max-age={max_age}, must-revalidate'
    return response
```

**Verwendung:**
```bash
# Erste Anfrage
curl -i http://localhost:5001/api/boxes
# Header: ETag: "abc123"

# Zweite Anfrage mit ETag
curl -i -H 'If-None-Match: "abc123"' http://localhost:5001/api/boxes
# Response: 304 Not Modified (keine Daten übertragen, spart Bandbreite)
```

---

### 3. Identification of Resources

**Implementierung:**
- Eindeutige URLs für jede Ressource
- URL-Struktur: `/api/boxes/{CODE}`
- CODE ist der eindeutige Identifier (Primary Key)

**Beispiele:**
```
/api/boxes              → Alle Kisten
/api/boxes/AB12         → Spezifische Kiste
/api/boxes/locations    → Alle Standorte
/api/boxes/stats        → Statistiken
```

---

### 4. Manipulation through Representations 

**Implementierung:**
- **JSON Format** für alle Daten
- `Content-Type: application/json` Header
- Vollständige Objekt-Repräsentation in Responses

**Beispiel:**
```json
// Request
POST /api/boxes
Content-Type: application/json

{
  "Location": "Küche",
  "Content": "Teller"
}

// Response
Content-Type: application/json

{
  "CODE": "AB12",
  "Location": "Küche",
  "Content": "Teller",
  ...
}
```

---

### 5. Self-Descriptive Messages

**Implementierung:**
- **Korrekte HTTP-Methoden:**
  - `GET`: Lesen von Daten
  - `POST`: Erstellen neuer Ressourcen
  - `PUT`: Aktualisieren existierender Ressourcen
  - `DELETE`: Löschen von Ressourcen

- **Passende Status Codes:**
  - `200 OK`: Erfolgreiche GET/PUT Anfrage
  - `201 Created`: Ressource erstellt
  - `204 No Content`: Erfolgreich gelöscht
  - `304 Not Modified`: Daten unverändert (Cache)
  - `400 Bad Request`: Ungültige Daten
  - `404 Not Found`: Ressource nicht gefunden
  - `500 Internal Server Error`: Serverfehler

- **Content-Type Header**: Immer gesetzt
- **Location Header**: Bei POST mit URL der neuen Ressource

**Code-Beispiel:**
```python
@app.route('/api/boxes', methods=['POST'])
def create_box():
    # ...
    response = make_response(jsonify(new_box), 201)  # Status 201
    response.headers['Location'] = f"/api/boxes/{code}"  # Location Header
    response.headers['Content-Type'] = 'application/json'
    return response
```

---

### 6. HATEOAS - Hypermedia as Engine of Application State 

**Implementierung:**
- Jede Response enthält `_links` mit verwandten Ressourcen
- Client kann API "entdecken" ohne URLs zu kennen
- Links zeigen verfügbare Aktionen

**Code-Beispiel:**
```python
def add_hateoas_links(box, code):
    box['_links'] = {
        'self': {'href': f'/api/boxes/{code}', 'method': 'GET'},
        'update': {'href': f'/api/boxes/{code}', 'method': 'PUT'},
        'delete': {'href': f'/api/boxes/{code}', 'method': 'DELETE'},
        'collection': {'href': '/api/boxes', 'method': 'GET'}
    }
    return box
```

**Beispiel-Response:**
```json
{
  "CODE": "AB12",
  "Location": "Küche",
  "_links": {
    "self": {
      "href": "/api/boxes/AB12",
      "method": "GET"
    },
    "update": {
      "href": "/api/boxes/AB12",
      "method": "PUT"
    },
    "delete": {
      "href": "/api/boxes/AB12",
      "method": "DELETE"
    },
    "collection": {
      "href": "/api/boxes",
      "method": "GET"
    }
  }
}
```

**Vorteil:**
Ein Client kann alle verfügbaren Aktionen aus den Links ablesen, ohne die API-Dokumentation zu kennen.

---

## Datenbank-Struktur

### Technologie
- **SQLite**: Leichtgewichtige, dateibasierte relationale Datenbank
- **Datei**: `boxes.db` (wird automatisch erstellt)

### Tabellen-Schema

```sql
CREATE TABLE boxes (
    CODE TEXT PRIMARY KEY NOT NULL,
    Location TEXT,
    Content TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

### Felder

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| `CODE` | TEXT | Eindeutiger Identifier (Primary Key) | "AB12" |
| `Location` | TEXT | Standort der Kiste (optional) | "Küche" |
| `Content` | TEXT | Inhalt der Kiste, getrennt durch Kommas (optional) | "Teller, Tassen, Besteck" |
| `created_at` | TEXT | Erstellungszeitpunkt (ISO Format) | "2026-02-16T10:30:00" |
| `updated_at` | TEXT | Letzter Update (ISO Format) | "2026-02-16T11:15:00" |

### CODE-Format

Der CODE wird automatisch generiert:
- 2 Großbuchstaben (A-Z)
- 2 Ziffern (0-9)
- Beispiele: AB12, XY45, QW89

**Warum dieses Format?**
- Kurz und einprägsam
- Leicht zu kommunizieren (z.B. am Telefon)
- 26×26×10×10 = 67.600 mögliche Kombinationen
- Deutlich unterscheidbar durch Mix aus Buchstaben und Zahlen

---

## Tests ausführen

### Voraussetzungen

1. Server muss laufen:
```bash
python box_server.py
```

2. In neuem Terminal Tests starten:
```bash
pytest test_boxes_api.py -v
```

### Test-Kategorien

Die Tests prüfen:

1. **CREATE Tests**
   - Kiste mit allen Daten erstellen
   - Kiste ohne Standort/Inhalt erstellen
   - Kiste mit eigenem CODE erstellen
   - Duplikat-CODE verhindern

2. **READ Tests**
   - Alle Kisten abrufen
   - Einzelne Kiste abrufen
   - Caching mit ETag
   - Standorte und Statistiken

3. **UPDATE Tests**
   - Standort ändern
   - Inhalt ändern
   - Beide Felder ändern
   - Nicht-existierende Kiste

4. **DELETE Tests**
   - Kiste löschen
   - Nicht-existierende Kiste

5. **REST-Prinzipien Tests**
   - Zustandslosigkeit
   - Content-Type Header
   - HATEOAS Links

### Test-Output

```
================================ test session starts =================================
test_boxes_api.py::TestCreateBox::test_create_box_with_all_data PASSED         [  5%]
test_boxes_api.py::TestCreateBox::test_create_box_without_location PASSED      [ 10%]
...
test_boxes_api.py::TestRESTPrinciples::test_hateoas_links_consistency PASSED   [100%]

================================ 25 passed in 2.45s ==================================
```

---

## Beispiele

### Beispiel-Workflow: Umzug einer Kiste

```bash
# 1. Neue Kiste erstellen
curl -X POST http://localhost:5001/api/boxes \
  -H "Content-Type: application/json" \
  -d '{"Location": "Wohnzimmer", "Content": "Bücher, DVDs"}'

# Response: {"CODE": "AB12", ...}

# 2. Kiste ins Arbeitszimmer verschieben
curl -X PUT http://localhost:5001/api/boxes/AB12 \
  -H "Content-Type: application/json" \
  -d '{"Location": "Arbeitszimmer"}'

# 3. Inhalt ergänzen
curl -X PUT http://localhost:5001/api/boxes/AB12 \
  -H "Content-Type: application/json" \
  -d '{"Content": "Bücher, DVDs, Notizblöcke"}'

# 4. Kiste später löschen
curl -X DELETE http://localhost:5001/api/boxes/AB12
```

### Beispiel: Alle Kisten in der Küche finden

```python
import requests

# Alle Kisten abrufen
response = requests.get('http://localhost:5001/api/boxes')
all_boxes = response.json()['boxes']

# Nach Küche filtern
kitchen_boxes = [box for box in all_boxes if box['Location'] == 'Küche']

for box in kitchen_boxes:
    print(f"Kiste {box['CODE']}: {box['Content']}")
```

---

## Technologie-Stack

- **Python 3.10**: Programmiersprache
- **Flask**: Web-Framework für die API
- **SQLite**: Datenbank
- **Pytest**: Test-Framework
- **Requests**: HTTP-Client für Tests

---

## Bewertung nach Kriterien

| Kriterium | Punkte | Status |
|-----------|--------|--------|
| REST: Zustandslosigkeit | 5 | Implementiert |
| REST: Caching | 5 | ETag, Cache-Control |
| REST: Identification of Resources | 5 | Eindeutige URLs |
| REST: Manipulation through Representations | 5 | JSON Format |
| REST: Self-Descriptive Messages | 10 | HTTP-Methoden, Status Codes |
| REST: HATEOAS | 10 | _links in allen Responses |
| Datenbank: Persistierung | 10 | SQLite |
| Testing: Vollständige Tests | 10 | 25+ Tests |
| CRUD: Vollständigkeit | 10 | Alle Operationen |
| Dokumentation: README | 10 | Dieses Dokument |
| **GESAMT** | **80** | **Vollständig** |

---

## Team

Mo, Arjen und Andrin

---

## Projekt-Informationen

- **Kurs**: Datenvernetzung in DB und Web
- **Abgabedatum**: 15. März 2026
- **Repository**: https://github.com/momu-m/BOXES_API

---

## Verwendung von KI

Bei der Entwicklung dieser API wurde KI (Claude) als Lernhilfe verwendet für:
- Verständnis von REST-Prinzipien
- Code-Struktur und Best Practices
- Test-Strategien
- Dokumentation

Alle generierten Inhalte wurden von uns geprüft, verstanden und angepasst.

---

## FAQ

**Q: Warum SQLite statt MySQL/PostgreSQL?**
A: SQLite ist einfacher einzurichten (keine Server notwendig) und perfekt für kleinere Projekte. Für produktive Anwendungen würde man zu MySQL/PostgreSQL wechseln.

**Q: Was passiert wenn der CODE-Pool aufgebraucht ist?**
A: Mit 67.600 möglichen Kombinationen ist das für ein Lagerverwaltungssystem sehr unwahrscheinlich. Bei Bedarf könnte man auf 3 Buchstaben + 3 Zahlen wechseln (17,5 Millionen Kombinationen).

**Q: Kann ich mehrere Inhalte in Content speichern?**
A: Ja! Content ist ein Textfeld, ihr könnt Inhalte mit Komma trennen: "Teller, Tassen, Besteck"

**Q: Wie kann ich die Datenbank zurücksetzen?**
A: Einfach die Datei `boxes.db` löschen. Beim nächsten Start wird sie neu erstellt.

---
