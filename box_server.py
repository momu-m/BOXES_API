"""
REST API Server fuer Kisten-Verwaltung
Autoren: Mohamad Murad, Arjen Hoti, Andrin Luethi

Swagger UI ist erreichbar unter: http://localhost:5001/apidocs
"""
from flask import Flask, request, jsonify, make_response
from flasgger import Swagger  # Swagger UI Bibliothek importieren
from boxes_repository import BoxesRepository
from datetime import datetime
import hashlib

app = Flask(__name__)

# ========================================
# SWAGGER UI KONFIGURATION
# ========================================
# Hier wird definiert, wie die Swagger UI aussieht und was sie anzeigt.
# 'specs_route' = Unter welcher URL die Swagger UI erreichbar ist
# 'title' = Der Titel, der oben in Swagger UI steht
# 'description' = Beschreibung des Projekts
# 'version' = Version der API
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",         # Interner Name fuer die Spezifikation
            "route": "/apispec.json",       # URL fuer die JSON-Spezifikation
            "rule_filter": lambda rule: True,  # Alle Endpunkte anzeigen
            "model_filter": lambda tag: True,  # Alle Modelle anzeigen
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,          # Swagger UI aktivieren
    "specs_route": "/apidocs"    # URL fuer Swagger UI -> http://localhost:5001/apidocs
}

# Allgemeine Informationen ueber die API (erscheinen oben in Swagger UI)
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Kisten-Verwaltungs REST-API",
        "description": (
            "Eine vollstaendige REST-API zur Verwaltung von Kisten mit Standort und Inhalt.\n\n"
            "Erstellt von **Mo, Arjen und Andrin** fuer den Kurs "
            "'Datenvernetzung in DB und Web'.\n\n"
            "## REST-Prinzipien\n"
            "Diese API implementiert alle geforderten REST-Prinzipien:\n"
            "- **Zustandslosigkeit** - Kein Session-State auf dem Server\n"
            "- **Caching** - ETag und Cache-Control Header\n"
            "- **Identification of Resources** - Eindeutige URLs\n"
            "- **Manipulation through Representations** - JSON Format\n"
            "- **Self-Descriptive Messages** - HTTP-Methoden und Status Codes\n"
            "- **HATEOAS** - Links in allen Responses\n\n"
            "## Datenbank\n"
            "SQLite mit automatischer CODE-Generierung (2 Buchstaben + 2 Zahlen, z.B. AB12)"
        ),
        "version": "1.0.0",
        "contact": {
            "name": "Gruppe: Mo, Arjen, Andrin"
        }
    },
    "host": "localhost:5001",          # Server-Adresse
    "basePath": "/",                   # Basis-Pfad
    "schemes": ["http"],               # Protokoll (HTTP)
    "tags": [
        {
            "name": "Kisten",
            "description": "CRUD-Operationen fuer Kisten (Erstellen, Lesen, Aktualisieren, Loeschen)"
        },
        {
            "name": "Zusatzfunktionen",
            "description": "Standorte und Statistiken"
        }
    ]
}

# Swagger UI initialisieren und mit der Flask-App verbinden
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Repository fuer Datenbank-Zugriff erstellen
boxes_repo = BoxesRepository()

# Basis-Pfad fuer alle API-Endpunkte
BASE_PATH = '/api/boxes'


# ========================================
# HILFSFUNKTIONEN
# ========================================

def add_hateoas_links(box, code):
    """
    Fuegt HATEOAS-Links zu einer Kiste hinzu
    HATEOAS = Hypermedia as the Engine of Application State

    Dies ermoeglicht es Clients, verwandte Ressourcen zu entdecken
    ohne die URL-Struktur kennen zu muessen.
    """
    box['_links'] = {
        'self': {
            'href': f'{BASE_PATH}/{code}',
            'method': 'GET'
        },
        'update': {
            'href': f'{BASE_PATH}/{code}',
            'method': 'PUT'
        },
        'delete': {
            'href': f'{BASE_PATH}/{code}',
            'method': 'DELETE'
        },
        'collection': {
            'href': BASE_PATH,
            'method': 'GET'
        }
    }
    return box


def calculate_etag(data):
    """
    Berechnet einen ETag (Entity Tag) fuer Caching

    Ein ETag ist ein eindeutiger Hash-Wert der Daten.
    Clients koennen damit pruefen, ob sich Daten geaendert haben.
    """
    data_str = str(data)
    return hashlib.md5(data_str.encode()).hexdigest()


def add_cache_headers(response, etag, max_age=60):
    """
    Fuegt Cache-Control Header zur Response hinzu

    Args:
        response: Flask Response Objekt
        etag: Entity Tag fuer die Daten
        max_age: Wie lange soll gecacht werden (in Sekunden)

    Cache-Control erklaert:
    - max-age: Wie lange sind die Daten frisch (in Sekunden)
    - must-revalidate: Client muss beim Server nachfragen ob Daten noch aktuell sind
    """
    response.headers['ETag'] = f'"{etag}"'
    response.headers['Cache-Control'] = f'max-age={max_age}, must-revalidate'
    response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response


# ========================================
# API ENDPUNKTE
# ========================================

@app.route(BASE_PATH, methods=['POST'])
def create_box():
    """
    Neue Kiste erstellen
    Erstellt eine neue Kiste in der Datenbank. Der CODE wird automatisch generiert
    (2 Buchstaben + 2 Zahlen), kann aber auch manuell angegeben werden.
    ---
    tags:
      - Kisten
    parameters:
      - in: body
        name: body
        description: Daten fuer die neue Kiste
        required: true
        schema:
          type: object
          properties:
            CODE:
              type: string
              description: Optionaler eigener CODE (z.B. AB12). Wird automatisch generiert wenn leer.
              example: "AB12"
            Location:
              type: string
              description: Standort der Kiste
              example: "Kueche"
            Content:
              type: string
              description: Inhalt der Kiste (mehrere Eintraege mit Komma trennen)
              example: "Teller, Tassen, Besteck"
    responses:
      201:
        description: Kiste wurde erfolgreich erstellt
        schema:
          type: object
          properties:
            CODE:
              type: string
              example: "AB12"
            Location:
              type: string
              example: "Kueche"
            Content:
              type: string
              example: "Teller, Tassen, Besteck"
            created_at:
              type: string
              example: "2026-02-16T10:30:00"
            updated_at:
              type: string
              example: "2026-02-16T10:30:00"
            _links:
              type: object
              description: HATEOAS-Links zu verwandten Aktionen
        headers:
          Location:
            type: string
            description: URL der neu erstellten Kiste
      400:
        description: "Fehler: CODE existiert bereits"
        schema:
          type: object
          properties:
            error:
              type: string
              example: "CODE existiert bereits"
            message:
              type: string
              example: "Eine Kiste mit diesem CODE existiert schon"
    """
    data = request.get_json()

    # Hole Daten aus Request (oder nutze Defaults)
    code = data.get('CODE') if data else None
    location = data.get('Location', '') if data else ''
    content = data.get('Content', '') if data else ''

    # Erstelle Kiste in Datenbank
    new_box = boxes_repo.create(code=code, location=location, content=content)

    if not new_box:
        # CODE existiert bereits
        return jsonify({
            'error': 'CODE existiert bereits',
            'message': 'Eine Kiste mit diesem CODE existiert schon'
        }), 400

    # Fuege HATEOAS-Links hinzu
    new_box = add_hateoas_links(new_box, new_box['CODE'])

    # Erstelle Response mit Location Header
    response = make_response(jsonify(new_box), 201)
    response.headers['Location'] = f"{BASE_PATH}/{new_box['CODE']}"
    response.headers['Content-Type'] = 'application/json'

    return response


@app.route(BASE_PATH, methods=['GET'])
def get_all_boxes():
    """
    Alle Kisten abrufen
    Gibt eine Liste aller Kisten in der Datenbank zurueck, inklusive
    HATEOAS-Links und Cache-Headern (ETag, Cache-Control).
    ---
    tags:
      - Kisten
    parameters:
      - in: header
        name: If-None-Match
        type: string
        description: ETag-Wert fuer Caching. Wenn die Daten sich nicht geaendert haben, kommt Status 304 zurueck.
        required: false
    responses:
      200:
        description: Liste aller Kisten
        schema:
          type: object
          properties:
            boxes:
              type: array
              items:
                type: object
                properties:
                  CODE:
                    type: string
                    example: "AB12"
                  Location:
                    type: string
                    example: "Kueche"
                  Content:
                    type: string
                    example: "Teller, Tassen"
                  created_at:
                    type: string
                    example: "2026-02-16T10:30:00"
                  updated_at:
                    type: string
                    example: "2026-02-16T10:30:00"
                  _links:
                    type: object
            total:
              type: integer
              example: 5
            _links:
              type: object
              description: HATEOAS-Links (self, create, locations, stats)
        headers:
          ETag:
            type: string
            description: Eindeutiger Hash-Wert fuer Caching
          Cache-Control:
            type: string
            description: "max-age=60, must-revalidate"
      304:
        description: Daten haben sich nicht geaendert (Cache-Treffer)
    """
    boxes = boxes_repo.get_all()

    # Fuege HATEOAS-Links zu jeder Kiste hinzu
    for box in boxes:
        box = add_hateoas_links(box, box['CODE'])

    # Erstelle Response-Daten mit Metainformationen
    response_data = {
        'boxes': boxes,
        'total': len(boxes),
        '_links': {
            'self': {
                'href': BASE_PATH,
                'method': 'GET'
            },
            'create': {
                'href': BASE_PATH,
                'method': 'POST'
            },
            'locations': {
                'href': f'{BASE_PATH}/locations',
                'method': 'GET'
            },
            'stats': {
                'href': f'{BASE_PATH}/stats',
                'method': 'GET'
            }
        }
    }

    # Berechne ETag fuer Caching
    etag = calculate_etag(boxes)

    # Pruefe ob Client bereits aktuelle Version hat
    if request.headers.get('If-None-Match') == f'"{etag}"':
        # 304 = Not Modified (Daten haben sich nicht geaendert)
        return '', 304

    # Erstelle Response mit Cache-Headern
    response = make_response(jsonify(response_data), 200)
    response.headers['Content-Type'] = 'application/json'
    response = add_cache_headers(response, etag)

    return response


@app.route(f'{BASE_PATH}/<code>', methods=['GET'])
def get_box(code):
    """
    Einzelne Kiste abrufen
    Gibt eine spezifische Kiste anhand ihres CODEs zurueck.
    Unterstuetzt Caching mit ETag-Headern.
    ---
    tags:
      - Kisten
    parameters:
      - in: path
        name: code
        type: string
        required: true
        description: Der eindeutige CODE der Kiste (z.B. AB12)
        example: "AB12"
      - in: header
        name: If-None-Match
        type: string
        description: ETag-Wert fuer Caching
        required: false
    responses:
      200:
        description: Die angeforderte Kiste
        schema:
          type: object
          properties:
            CODE:
              type: string
              example: "AB12"
            Location:
              type: string
              example: "Kueche"
            Content:
              type: string
              example: "Teller, Tassen, Besteck"
            created_at:
              type: string
              example: "2026-02-16T10:30:00"
            updated_at:
              type: string
              example: "2026-02-16T10:30:00"
            _links:
              type: object
              description: HATEOAS-Links (self, update, delete, collection)
        headers:
          ETag:
            type: string
            description: Eindeutiger Hash-Wert fuer Caching
      304:
        description: Daten haben sich nicht geaendert (Cache-Treffer)
      404:
        description: Kiste wurde nicht gefunden
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Nicht gefunden"
            message:
              type: string
              example: "Kiste mit CODE AB12 existiert nicht"
    """
    box = boxes_repo.get(code)

    if not box:
        return jsonify({
            'error': 'Nicht gefunden',
            'message': f'Kiste mit CODE {code} existiert nicht'
        }), 404

    # Fuege HATEOAS-Links hinzu
    box = add_hateoas_links(box, code)

    # Berechne ETag
    etag = calculate_etag(box)

    # Pruefe If-None-Match Header
    if request.headers.get('If-None-Match') == f'"{etag}"':
        return '', 304

    # Erstelle Response mit Cache-Headern
    response = make_response(jsonify(box), 200)
    response.headers['Content-Type'] = 'application/json'
    response = add_cache_headers(response, etag)

    return response


@app.route(f'{BASE_PATH}/<code>', methods=['PUT'])
def update_box(code):
    """
    Kiste aktualisieren
    Aktualisiert den Standort und/oder den Inhalt einer bestehenden Kiste.
    Man kann nur die Felder senden, die man aendern moechte.
    ---
    tags:
      - Kisten
    parameters:
      - in: path
        name: code
        type: string
        required: true
        description: Der eindeutige CODE der Kiste (z.B. AB12)
        example: "AB12"
      - in: body
        name: body
        description: Felder die aktualisiert werden sollen
        required: true
        schema:
          type: object
          properties:
            Location:
              type: string
              description: Neuer Standort der Kiste
              example: "Keller"
            Content:
              type: string
              description: Neuer Inhalt der Kiste
              example: "Werkzeug, Schrauben"
    responses:
      200:
        description: Kiste wurde erfolgreich aktualisiert
        schema:
          type: object
          properties:
            CODE:
              type: string
              example: "AB12"
            Location:
              type: string
              example: "Keller"
            Content:
              type: string
              example: "Werkzeug, Schrauben"
            created_at:
              type: string
              example: "2026-02-16T10:30:00"
            updated_at:
              type: string
              example: "2026-02-16T11:15:00"
            _links:
              type: object
              description: HATEOAS-Links
      400:
        description: "Fehler: Request-Body ist leer"
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Keine Daten"
            message:
              type: string
              example: "Request-Body darf nicht leer sein"
      404:
        description: Kiste wurde nicht gefunden
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Nicht gefunden"
            message:
              type: string
              example: "Kiste mit CODE AB12 existiert nicht"
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'Keine Daten',
            'message': 'Request-Body darf nicht leer sein'
        }), 400

    # Update durchfuehren
    updated_box = boxes_repo.update(
        code=code,
        location=data.get('Location'),
        content=data.get('Content')
    )

    if not updated_box:
        return jsonify({
            'error': 'Nicht gefunden',
            'message': f'Kiste mit CODE {code} existiert nicht'
        }), 404

    # Fuege HATEOAS-Links hinzu
    updated_box = add_hateoas_links(updated_box, code)

    response = make_response(jsonify(updated_box), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


@app.route(f'{BASE_PATH}/<code>', methods=['DELETE'])
def delete_box(code):
    """
    Kiste loeschen
    Loescht eine Kiste permanent aus der Datenbank.
    Bei Erfolg kommt Status 204 (No Content) ohne Body zurueck.
    ---
    tags:
      - Kisten
    parameters:
      - in: path
        name: code
        type: string
        required: true
        description: Der eindeutige CODE der Kiste die geloescht werden soll
        example: "AB12"
    responses:
      204:
        description: Kiste wurde erfolgreich geloescht (kein Body)
      404:
        description: Kiste wurde nicht gefunden
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Nicht gefunden"
            message:
              type: string
              example: "Kiste mit CODE AB12 existiert nicht"
    """
    success = boxes_repo.delete(code)

    if not success:
        return jsonify({
            'error': 'Nicht gefunden',
            'message': f'Kiste mit CODE {code} existiert nicht'
        }), 404

    # 204 = No Content (erfolgreich geloescht, kein Body notwendig)
    return '', 204


# ========================================
# ZUSAETZLICHE ENDPUNKTE (fuer erweiterte Funktionalitaet)
# ========================================

@app.route(f'{BASE_PATH}/locations', methods=['GET'])
def get_locations():
    """
    Alle Standorte abrufen
    Gibt eine Liste aller eindeutigen Standorte zurueck, an denen Kisten stehen.
    ---
    tags:
      - Zusatzfunktionen
    responses:
      200:
        description: Liste aller Standorte
        schema:
          type: object
          properties:
            locations:
              type: array
              items:
                type: string
              example: ["Kueche", "Keller", "Garage"]
            total:
              type: integer
              example: 3
            _links:
              type: object
              description: HATEOAS-Links (self, collection)
    """
    locations = boxes_repo.get_all_locations()

    response_data = {
        'locations': locations,
        'total': len(locations),
        '_links': {
            'self': {
                'href': f'{BASE_PATH}/locations',
                'method': 'GET'
            },
            'collection': {
                'href': BASE_PATH,
                'method': 'GET'
            }
        }
    }

    response = make_response(jsonify(response_data), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


@app.route(f'{BASE_PATH}/stats', methods=['GET'])
def get_stats():
    """
    Statistiken abrufen
    Gibt Statistiken ueber die Kisten-Verwaltung zurueck:
    Gesamtanzahl der Kisten und Anzahl der verschiedenen Standorte.
    ---
    tags:
      - Zusatzfunktionen
    responses:
      200:
        description: Statistiken ueber die Kisten
        schema:
          type: object
          properties:
            total_boxes:
              type: integer
              description: Gesamtanzahl der Kisten
              example: 15
            total_locations:
              type: integer
              description: Anzahl verschiedener Standorte
              example: 5
            _links:
              type: object
              description: HATEOAS-Links (self, collection, locations)
    """
    stats = {
        'total_boxes': boxes_repo.count_boxes(),
        'total_locations': boxes_repo.count_locations(),
        '_links': {
            'self': {
                'href': f'{BASE_PATH}/stats',
                'method': 'GET'
            },
            'collection': {
                'href': BASE_PATH,
                'method': 'GET'
            },
            'locations': {
                'href': f'{BASE_PATH}/locations',
                'method': 'GET'
            }
        }
    }

    response = make_response(jsonify(stats), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(error):
    """Handler fuer 404 Fehler"""
    return jsonify({
        'error': 'Nicht gefunden',
        'message': 'Der angefragte Endpunkt existiert nicht'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler fuer 500 Fehler"""
    return jsonify({
        'error': 'Serverfehler',
        'message': 'Ein interner Fehler ist aufgetreten'
    }), 500


if __name__ == '__main__':
    # Beim Starten wird eine Info ausgegeben, damit ihr wisst wo Swagger UI ist
    print("=" * 60)
    print("  Kisten-Verwaltungs REST-API")
    print("  API:        http://localhost:5001/api/boxes")
    print("  Swagger UI: http://localhost:5001/apidocs")
    print("=" * 60)
    # Port 5001 statt 5000, weil macOS AirPlay Receiver Port 5000 blockiert
    app.run(host='0.0.0.0', port=5001, debug=True)
