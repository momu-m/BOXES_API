"""
REST API Server für Kisten-Verwaltung
Implementiert alle REST-Prinzipien:
- Zustandslosigkeit
- Caching
- Uniform Interface (Identification, Manipulation, Self-Descriptive, HATEOAS)
"""
from flask import Flask, request, jsonify, make_response
from boxes_repository import BoxesRepository
from datetime import datetime
import hashlib

app = Flask(__name__)
boxes_repo = BoxesRepository()

# Basis-Pfad für alle API-Endpunkte
BASE_PATH = '/api/boxes'


# ========================================
# HILFSFUNKTIONEN
# ========================================

def add_hateoas_links(box, code):
    """
    Fügt HATEOAS-Links zu einer Kiste hinzu
    HATEOAS = Hypermedia as the Engine of Application State
    
    Dies ermöglicht es Clients, verwandte Ressourcen zu entdecken
    ohne die URL-Struktur kennen zu müssen.
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
    Berechnet einen ETag (Entity Tag) für Caching
    
    Ein ETag ist ein eindeutiger Hash-Wert der Daten.
    Clients können damit prüfen, ob sich Daten geändert haben.
    """
    data_str = str(data)
    return hashlib.md5(data_str.encode()).hexdigest()


def add_cache_headers(response, etag, max_age=60):
    """
    Fügt Cache-Control Header zur Response hinzu
    
    Args:
        response: Flask Response Objekt
        etag: Entity Tag für die Daten
        max_age: Wie lange soll gecacht werden (in Sekunden)
    
    Cache-Control erklärt:
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
    Erstellt eine neue Kiste
    
    REST-Prinzipien:
    - Self-Descriptive: POST Methode = Erstellen
    - Status 201: Created (Ressource wurde erstellt)
    - Location Header: Wo die neue Ressource zu finden ist
    - HATEOAS: Links zu verwandten Aktionen
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
    
    # Füge HATEOAS-Links hinzu
    new_box = add_hateoas_links(new_box, new_box['CODE'])
    
    # Erstelle Response mit Location Header
    response = make_response(jsonify(new_box), 201)
    response.headers['Location'] = f"{BASE_PATH}/{new_box['CODE']}"
    response.headers['Content-Type'] = 'application/json'
    
    return response


@app.route(BASE_PATH, methods=['GET'])
def get_all_boxes():
    """
    Holt alle Kisten
    
    REST-Prinzipien:
    - Self-Descriptive: GET Methode = Lesen
    - Caching: ETag und Cache-Control Header
    - HATEOAS: Links zu jeder Kiste
    """
    boxes = boxes_repo.get_all()
    
    # Füge HATEOAS-Links zu jeder Kiste hinzu
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
    
    # Berechne ETag für Caching
    etag = calculate_etag(boxes)
    
    # Prüfe ob Client bereits aktuelle Version hat
    if request.headers.get('If-None-Match') == f'"{etag}"':
        # 304 = Not Modified (Daten haben sich nicht geändert)
        return '', 304
    
    # Erstelle Response mit Cache-Headern
    response = make_response(jsonify(response_data), 200)
    response.headers['Content-Type'] = 'application/json'
    response = add_cache_headers(response, etag)
    
    return response


@app.route(f'{BASE_PATH}/<code>', methods=['GET'])
def get_box(code):
    """
    Holt eine spezifische Kiste
    
    REST-Prinzipien:
    - Identification of Resources: Eindeutige URL /api/boxes/{CODE}
    - Self-Descriptive: GET Methode = Lesen
    - HATEOAS: Links zu möglichen Aktionen
    - Caching: ETag Header
    """
    box = boxes_repo.get(code)
    
    if not box:
        return jsonify({
            'error': 'Nicht gefunden',
            'message': f'Kiste mit CODE {code} existiert nicht'
        }), 404
    
    # Füge HATEOAS-Links hinzu
    box = add_hateoas_links(box, code)
    
    # Berechne ETag
    etag = calculate_etag(box)
    
    # Prüfe If-None-Match Header
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
    Aktualisiert eine Kiste
    
    REST-Prinzipien:
    - Self-Descriptive: PUT Methode = Vollständiges Update
    - Manipulation through Representations: JSON wird akzeptiert und zurückgegeben
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Keine Daten',
            'message': 'Request-Body darf nicht leer sein'
        }), 400
    
    # Update durchführen
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
    
    # Füge HATEOAS-Links hinzu
    updated_box = add_hateoas_links(updated_box, code)
    
    response = make_response(jsonify(updated_box), 200)
    response.headers['Content-Type'] = 'application/json'
    
    return response


@app.route(f'{BASE_PATH}/<code>', methods=['DELETE'])
def delete_box(code):
    """
    Löscht eine Kiste
    
    REST-Prinzipien:
    - Self-Descriptive: DELETE Methode = Löschen
    - Status 204: No Content (erfolgreich gelöscht, keine Daten zurück)
    - Status 404: Not Found (Kiste existiert nicht)
    """
    success = boxes_repo.delete(code)
    
    if not success:
        return jsonify({
            'error': 'Nicht gefunden',
            'message': f'Kiste mit CODE {code} existiert nicht'
        }), 404
    
    # 204 = No Content (erfolgreich gelöscht, kein Body notwendig)
    return '', 204


# ========================================
# ZUSÄTZLICHE ENDPUNKTE (für erweiterte Funktionalität)
# ========================================

@app.route(f'{BASE_PATH}/locations', methods=['GET'])
def get_locations():
    """
    Gibt alle Standorte zurück
    
    HATEOAS: Diese Ressource ist über Links in /api/boxes erreichbar
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
    Gibt Statistiken über die Kisten zurück
    
    HATEOAS: Diese Ressource ist über Links in /api/boxes erreichbar
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
    """Handler für 404 Fehler"""
    return jsonify({
        'error': 'Nicht gefunden',
        'message': 'Der angefragte Endpunkt existiert nicht'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler für 500 Fehler"""
    return jsonify({
        'error': 'Serverfehler',
        'message': 'Ein interner Fehler ist aufgetreten'
    }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
