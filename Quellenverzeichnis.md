# Quellenverzeichnis für das BOXES_API REST Projekt

Arjen:
Diese Quellen wurden mit Notion erfasst und während der Arbeit laufend ergänzt. Aus dem Grund handelt es sich um ein einzigen commit. Die Daten wurden nach 
Fertigstellung importiert.

---

## Konsumierte Videos
 Nr. | Thema | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----|-----------|
| V1 | `Flask` | **build a meme Python website (Flask Tutorial for Beginners)** | https://www.youtube.com/watch?v=5aYpkLfkgRE | Erklärt wie Flask funktioniert und die Grundlagen des Frameworks. |
| V2 | `Flask` | **Python REST API Tutorial for Beginners - How to Build a Flask REST API** | https://www.youtube.com/watch?v=z3YMz-Gocmw | Erklärt Aufbau und funktion von Flask mit REST Prinzipien. |
| V3 | `ETag` | **REST API Cache & Synchronisation mit ETag Header – API Caching Folge 3** | https://www.youtube.com/watch?v=KodZcgWYGfg | EGrundlagen der ETags |
| V4 | `ETag` | **ETag vs Last-Modified HTTP Headers Explained** | https://www.youtube.com/watch?v=NMSYYTNLm9E | Unterschiede ETags und Last Modified und deren verwendung |
| V5 | `Swagger` | **How to Add Swagger to Flask APIs (2024)** | https://www.youtube.com/watch?v=Oqg83g4khzc | Vorgehen zum einbinden von Swagger UI in Flask |
| V6 | `SQL Python` | **Preventing SQL Injection in Python** | https://www.youtube.com/watch?v=1cQy9N1Xndk | Vorgehen zum einbinden von Swagger UI in Flask |

## Flask Framework

| Nr. | Konzept | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----|-----------|
| 1 | `app = Flask(__name__)` | **Quickstart - Flask Documentation** | https://flask.palletsprojects.com/en/stable/quickstart/ | Erklärt das Erstellen einer Flask-App-Instanz mit `Flask(__name__)` und die Grundlagen des Frameworks. |
| 2 | `@app.route()` mit HTTP-Methoden | **Quickstart: HTTP Methods - Flask Documentation** | https://flask.palletsprojects.com/en/stable/quickstart/#http-methods | Beschreibt den `@app.route()`-Dekorator mit HTTP-Methoden (GET, POST, PUT, DELETE) für URL-Routing. |
| 3 | `request.get_json()` | **API: Request.get_json - Flask Documentation** | https://flask.palletsprojects.com/en/stable/api/#flask.Request.get_json | Dokumentiert `request.get_json()` zum Parsen von JSON-Daten aus eingehenden HTTP-Anfragen. |
| 4a | `make_response()` | **API: flask.make_response - Flask Documentation** | https://flask.palletsprojects.com/en/stable/api/#flask.make_response | Dokumentiert `make_response()` zum Erstellen benutzerdefinierter Response-Objekte mit Headers und Statuscodes. |
| 4b | `jsonify()` | **API: flask.json.jsonify - Flask Documentation** | https://flask.palletsprojects.com/en/stable/api/#flask.json.jsonify | Dokumentiert `jsonify()` zur Serialisierung von Python-Daten als JSON-Response. |
| 5 | `@app.errorhandler(404/500)` | **Handling Application Errors - Flask Documentation** | https://flask.palletsprojects.com/en/stable/errorhandling/ | Beschreibt die Registrierung von Fehlerbehandlern mit `@app.errorhandler()` für HTTP-Fehlercodes wie 404 und 500. |
| 6 | Flasgger / Swagger UI | **flasgger/flasgger - GitHub** | https://github.com/flasgger/flasgger | Flask-Erweiterung zur Konfiguration von `swagger_config`, `swagger_template` und Einbettung der Swagger-UI für REST-APIs. |
| 24 | `app.run(host, port, debug)` | **API: Flask.run - Flask Documentation** | https://flask.palletsprojects.com/en/stable/api/#flask.Flask.run | Dokumentiert `app.run()` mit Parametern `host='0.0.0.0'`, `port` und `debug` zum Starten des Entwicklungsservers. |

---

## REST- und HTTP-Konzepte

| Nr. | Konzept | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----------|------------------------|
| 7 | HATEOAS-Links in REST APIs | **How to Build HATEOAS Driven REST APIs - restfulapi.net** | https://restfulapi.net/hateoas/ | Erklärt das HATEOAS-Prinzip und zeigt, wie man `_links`-Hypermedia-Verknüpfungen in JSON-Antworten einfügt. |
| 8 | ETag / If-None-Match / 304 | **ETag header - HTTP · MDN Web Docs** | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag | MDN-Referenz zum ETag-Header für Ressourcen-Versionierung, If-None-Match-Validierung und 304 Not Modified. |
| 9 | Cache-Control: max-age, must-revalidate | **Cache-Control header - HTTP · MDN Web Docs** | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control | Offizielle MDN-Dokumentation zum Cache-Control-Header mit allen Direktiven inkl. max-age und must-revalidate. |
| 21 | HTTP Status Codes (200–500) | **HTTP response status codes - MDN Web Docs** | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status | Vollständige Übersicht aller HTTP-Statuscodes (200, 201, 204, 304, 400, 404, 500 u. a.) mit Erklärungen. |
| 22 | REST-Prinzipien allgemein | **REST Architectural Constraints - restfulapi.net** | https://restfulapi.net/rest-architectural-constraints/ | Beschreibt die sechs REST-Prinzipien nach Fielding: Uniform Interface, Statelessness, Caching, Client-Server, Layered System, Code on Demand. |

---

## Python Standardbibliothek

| Nr. | Konzept | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----|-----------|
| 10 | `hashlib.md5().hexdigest()` | **hashlib - Secure hashes and message digests** | https://docs.python.org/3/library/hashlib.html | Dokumentiert sichere Hash-Algorithmen wie MD5 und SHA-256 inkl. der Methode `hexdigest()` zur Erzeugung hexadezimaler Hash-Werte. |
| 11 | `sqlite3.connect()`, `cursor()`, `commit()`, `close()` | **sqlite3 - DB-API 2.0 interface for SQLite databases** | https://docs.python.org/3/library/sqlite3.html | Offizielle Dokumentation des sqlite3-Moduls mit allen Funktionen für die SQLite-Datenbankanbindung in Python. |
| 12 | `conn.row_factory = sqlite3.Row` | **sqlite3.Row - Python Documentation** | https://docs.python.org/3/library/sqlite3.html#sqlite3.Row | Beschreibt die `Row`-Klasse und `row_factory` für den spaltenbasierten Zugriff auf Abfrageergebnisse per Name statt Index. |
| 13a | Parametrisierte SQL-Queries `(?, ?)` | **sqlite3 - How to use placeholders - Python Documentation** | https://docs.python.org/3/library/sqlite3.html | Erklärung der parametrisierten Queries mit `?`-Platzhaltern im sqlite3-Modul zur Vermeidung von SQL-Injection. |
| 13b | SQL Injection Prevention | **Bobby Tables: A guide to preventing SQL injection > Python** | https://bobby-tables.com/python | Praxisleitfaden zur Vermeidung von SQL-Injection in Python mit Beispielen für verschiedene Datenbanktreiber. |
| 14 | `sqlite3.IntegrityError` | **sqlite3.IntegrityError - Python Documentation** | https://docs.python.org/3/library/sqlite3.html#sqlite3.IntegrityError | Dokumentiert die Ausnahme `IntegrityError`, die bei Verletzung von Integritätsbedingungen (z. B. UNIQUE/PRIMARY KEY) ausgelöst wird. |
| 15 | `cursor.rowcount` | **sqlite3.Cursor.rowcount - Python Documentation** | https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.rowcount | Beschreibt das `rowcount`-Attribut, das die Anzahl der durch DELETE/UPDATE/INSERT betroffenen Zeilen zurückgibt. |
| 16 | `random.choices()` | **random.choices - Python Documentation** | https://docs.python.org/3/library/random.html#random.choices | Dokumentiert `random.choices()` für gewichtete Zufallsauswahl mit Zurücklegen, z. B. kombiniert mit `string.ascii_uppercase`. |
| 17 | `datetime.now().isoformat()` | **datetime.datetime.isoformat - Python Documentation** | https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat | Dokumentiert die `isoformat()`-Methode zur Ausgabe von Datum und Uhrzeit im ISO-8601-Format. |
| 23 | `if __name__ == '__main__':` | **\_\_main\_\_ - Top-level code environment - Python Documentation** | https://docs.python.org/3/library/__main__.html | Erklärt das `if __name__ == '__main__':`-Muster und die Rolle des `__main__`-Moduls als Einstiegspunkt. |
| 26 | `string.ascii_uppercase`, `string.digits` | **string - Common string operations - Python Documentation** | https://docs.python.org/3/library/string.html | Dokumentiert das `string`-Modul mit Konstanten wie `ascii_uppercase` ('A–Z') und `digits` ('0–9'). |

---

## SQLite (offizielle Doku)

| Nr. | Konzept | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----|-----------|
| 25 | `SELECT DISTINCT` | **SELECT - SQLite Documentation** | https://www.sqlite.org/lang_select.html | Offizielle SQLite-Dokumentation der SELECT-Anweisung einschliesslich der DISTINCT-Klausel zur Entfernung doppelter Ergebniszeilen. |

---

## Testing und externe Bibliotheken

| Nr. | Konzept | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----|-----------|
| 19 | pytest Fixtures (`scope="session"`, `yield`) | **How to use fixtures - pytest Documentation** | https://docs.pytest.org/en/stable/how-to/fixtures.html | Offizielle Doku zu pytest-Fixtures mit Scopes (session, module, class, function), yield-basiertem Setup/Teardown und Finalisierung. |
| 20 | `requests`-Bibliothek (GET, POST, PUT, DELETE) | **Quickstart - Requests Documentation** | https://requests.readthedocs.io/en/latest/user/quickstart/ | Schnellstart-Anleitung für HTTP-Anfragen mit der Python-requests-Bibliothek inkl. Beispielen zu GET, POST, PUT, DELETE. |

---

## Design Patterns

| Nr. | Konzept | Quelle / Titel | URL | Beschrieb |
|-----|---------|----------------|-----|-----------|
| 18a | Python-Klassen mit `__init__` | **9. Classes - Python 3 Tutorial** | https://docs.python.org/3/tutorial/classes.html | Offizielles Python-Tutorial zu Klassen, der `__init__`-Methode, Instanzattributen und Vererbung. |
| 18b | Repository Pattern | **Repository - Martin Fowler (PoEAA Catalog)** | https://martinfowler.com/eaaCatalog/repository.html | Martin Fowlers Definition des Repository-Patterns als Abstraktion der Datenzugriffsschicht mit sammlungsartigem Interface. |

---

