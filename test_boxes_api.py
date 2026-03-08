"""
Tests für die Boxes REST API
Autoren: Mohamad Murad, Arjen Hoti, Andrin Luethi

Diese Tests prüfen:
- Alle CRUD-Operationen (Create, Read, Update, Delete)
- REST-Prinzipien (HATEOAS, Caching, Status Codes)
- Error Handling
"""
import pytest
import requests
import time

BASE_URL = "http://localhost:5001"
API_PATH = "/api/boxes"


# ========================================
# FIXTURES (Test-Hilfsmittel)
# ========================================

@pytest.fixture(scope="session")
def base_url():
    """Gibt die Basis-URL der API zurück"""
    return BASE_URL


@pytest.fixture(scope="session")
def boxes_endpoint(base_url):
    """Gibt den vollständigen Endpunkt zurück"""
    return f"{base_url}{API_PATH}"


@pytest.fixture
def test_box(boxes_endpoint):
    """
    Erstellt eine Test-Kiste für Tests und löscht sie danach
    
    Verwendung in Tests:
    def test_something(test_box):
        code = test_box['code']
        location = test_box['location']
    """
    # Setup: Erstelle Test-Kiste
    test_data = {
        "Location": "Testkeller",
        "Content": "Testinhalt, Testschuhe"
    }
    
    response = requests.post(boxes_endpoint, json=test_data)
    box_code = response.json()['CODE']
    box_location = response.headers.get('Location')
    
    yield {
        'code': box_code,
        'location_url': box_location,
        'data': test_data
    }
    
    # Teardown: Lösche Test-Kiste
    try:
        requests.delete(f"{boxes_endpoint}/{box_code}")
    except:
        pass  # Kiste wurde möglicherweise schon gelöscht


# ========================================
# CREATE TESTS (POST)
# ========================================

class TestCreateBox:
    """Tests für das Erstellen von Kisten"""
    
    def test_create_box_with_all_data(self, boxes_endpoint):
        """Test: Kiste mit allen Daten erstellen"""
        data = {
            "Location": "Küche",
            "Content": "Teller, Tassen, Besteck"
        }
        
        response = requests.post(boxes_endpoint, json=data)
        result = response.json()
        
        # Prüfe Status Code
        assert response.status_code == 201, "Status sollte 201 (Created) sein"
        
        # Prüfe ob Location Header gesetzt ist
        assert 'Location' in response.headers, "Location Header sollte vorhanden sein"
        
        # Prüfe ob CODE generiert wurde
        assert 'CODE' in result, "CODE sollte vorhanden sein"
        assert len(result['CODE']) == 4, "CODE sollte 4 Zeichen lang sein"
        
        # Prüfe ob Daten korrekt gespeichert wurden
        assert result['Location'] == data['Location']
        assert result['Content'] == data['Content']
        
        # Prüfe HATEOAS Links
        assert '_links' in result, "HATEOAS Links sollten vorhanden sein"
        assert 'self' in result['_links']
        assert 'update' in result['_links']
        assert 'delete' in result['_links']
        
        # Cleanup
        requests.delete(f"{boxes_endpoint}/{result['CODE']}")
    
    def test_create_box_without_location(self, boxes_endpoint):
        """Test: Kiste ohne Standort erstellen"""
        data = {
            "Content": "Nur Inhalt"
        }
        
        response = requests.post(boxes_endpoint, json=data)
        result = response.json()
        
        assert response.status_code == 201
        assert result['Location'] == ""
        assert result['Content'] == data['Content']
        
        # Cleanup
        requests.delete(f"{boxes_endpoint}/{result['CODE']}")
    
    def test_create_box_without_content(self, boxes_endpoint):
        """Test: Kiste ohne Inhalt erstellen"""
        data = {
            "Location": "Garage"
        }
        
        response = requests.post(boxes_endpoint, json=data)
        result = response.json()
        
        assert response.status_code == 201
        assert result['Location'] == data['Location']
        assert result['Content'] == ""
        
        # Cleanup
        requests.delete(f"{boxes_endpoint}/{result['CODE']}")
    
    def test_create_box_empty(self, boxes_endpoint):
        """Test: Leere Kiste erstellen"""
        response = requests.post(boxes_endpoint, json={})
        result = response.json()
        
        assert response.status_code == 201
        assert 'CODE' in result
        
        # Cleanup
        requests.delete(f"{boxes_endpoint}/{result['CODE']}")
    
    def test_create_box_with_custom_code(self, boxes_endpoint):
        """Test: Kiste mit eigenem CODE erstellen"""
        data = {
            "CODE": "ZZ99",
            "Location": "Test"
        }
        
        response = requests.post(boxes_endpoint, json=data)
        result = response.json()
        
        assert response.status_code == 201
        assert result['CODE'] == "ZZ99"
        
        # Cleanup
        requests.delete(f"{boxes_endpoint}/{result['CODE']}")
    
    def test_create_box_duplicate_code(self, boxes_endpoint):
        """Test: Versuch einen duplizierten CODE zu erstellen"""
        data = {
            "CODE": "DUP1",
            "Location": "Erste Kiste"
        }
        
        # Erstelle erste Kiste
        response1 = requests.post(boxes_endpoint, json=data)
        assert response1.status_code == 201
        
        # Versuche zweite Kiste mit gleichem CODE zu erstellen
        response2 = requests.post(boxes_endpoint, json=data)
        
        assert response2.status_code == 400, "Sollte 400 (Bad Request) sein"
        assert 'error' in response2.json()
        
        # Cleanup
        requests.delete(f"{boxes_endpoint}/DUP1")


# ========================================
# READ TESTS (GET)
# ========================================

class TestReadBoxes:
    """Tests für das Lesen von Kisten"""
    
    def test_get_all_boxes(self, boxes_endpoint, test_box):
        """Test: Alle Kisten abrufen"""
        response = requests.get(boxes_endpoint)
        result = response.json()
        
        assert response.status_code == 200
        assert 'boxes' in result
        assert 'total' in result
        assert isinstance(result['boxes'], list)
        
        # Prüfe HATEOAS Links
        assert '_links' in result
        assert 'self' in result['_links']
        assert 'create' in result['_links']
        
        # Prüfe Cache Headers
        assert 'ETag' in response.headers, "ETag Header sollte vorhanden sein"
        assert 'Cache-Control' in response.headers, "Cache-Control Header sollte vorhanden sein"
    
    def test_get_all_boxes_caching(self, boxes_endpoint):
        """Test: Caching mit If-None-Match Header"""
        # Erste Anfrage
        response1 = requests.get(boxes_endpoint)
        etag = response1.headers.get('ETag')
        
        assert etag is not None, "ETag sollte vorhanden sein"
        
        # Zweite Anfrage mit If-None-Match Header
        headers = {'If-None-Match': etag}
        response2 = requests.get(boxes_endpoint, headers=headers)
        
        assert response2.status_code == 304, "Status sollte 304 (Not Modified) sein"
    
    def test_get_specific_box(self, boxes_endpoint, test_box):
        """Test: Spezifische Kiste abrufen"""
        response = requests.get(f"{boxes_endpoint}/{test_box['code']}")
        result = response.json()
        
        assert response.status_code == 200
        assert result['CODE'] == test_box['code']
        assert result['Location'] == test_box['data']['Location']
        
        # Prüfe HATEOAS Links
        assert '_links' in result
        assert 'self' in result['_links']
        assert 'update' in result['_links']
        assert 'delete' in result['_links']
        
        # Prüfe Cache Headers
        assert 'ETag' in response.headers
    
    def test_get_nonexistent_box(self, boxes_endpoint):
        """Test: Nicht existierende Kiste abrufen"""
        response = requests.get(f"{boxes_endpoint}/XXXX")
        
        assert response.status_code == 404
        assert 'error' in response.json()
    
    def test_get_locations(self, boxes_endpoint, test_box):
        """Test: Alle Standorte abrufen"""
        response = requests.get(f"{boxes_endpoint}/locations")
        result = response.json()
        
        assert response.status_code == 200
        assert 'locations' in result
        assert 'total' in result
        assert isinstance(result['locations'], list)
        
        # Test-Standort sollte enthalten sein
        assert test_box['data']['Location'] in result['locations']
    
    def test_get_stats(self, boxes_endpoint, test_box):
        """Test: Statistiken abrufen"""
        response = requests.get(f"{boxes_endpoint}/stats")
        result = response.json()
        
        assert response.status_code == 200
        assert 'total_boxes' in result
        assert 'total_locations' in result
        assert result['total_boxes'] > 0  # Mindestens die Test-Kiste
        
        # Prüfe HATEOAS Links
        assert '_links' in result


# ========================================
# UPDATE TESTS (PUT)
# ========================================

class TestUpdateBox:
    """Tests für das Aktualisieren von Kisten"""
    
    def test_update_location(self, boxes_endpoint, test_box):
        """Test: Standort einer Kiste ändern"""
        update_data = {
            "Location": "Neuer Standort"
        }
        
        response = requests.put(
            f"{boxes_endpoint}/{test_box['code']}",
            json=update_data
        )
        result = response.json()
        
        assert response.status_code == 200
        assert result['Location'] == "Neuer Standort"
        # Content sollte unverändert bleiben
        assert result['Content'] == test_box['data']['Content']
    
    def test_update_content(self, boxes_endpoint, test_box):
        """Test: Inhalt einer Kiste ändern"""
        update_data = {
            "Content": "Neuer Inhalt, Weitere Items"
        }
        
        response = requests.put(
            f"{boxes_endpoint}/{test_box['code']}",
            json=update_data
        )
        result = response.json()
        
        assert response.status_code == 200
        assert result['Content'] == "Neuer Inhalt, Weitere Items"
        # Location sollte unverändert bleiben
        assert result['Location'] == test_box['data']['Location']
    
    def test_update_both(self, boxes_endpoint, test_box):
        """Test: Standort und Inhalt ändern"""
        update_data = {
            "Location": "Komplett neu",
            "Content": "Alles neu"
        }
        
        response = requests.put(
            f"{boxes_endpoint}/{test_box['code']}",
            json=update_data
        )
        result = response.json()
        
        assert response.status_code == 200
        assert result['Location'] == "Komplett neu"
        assert result['Content'] == "Alles neu"
    
    def test_update_nonexistent_box(self, boxes_endpoint):
        """Test: Nicht existierende Kiste aktualisieren"""
        update_data = {
            "Location": "Test"
        }
        
        response = requests.put(f"{boxes_endpoint}/XXXX", json=update_data)
        
        assert response.status_code == 404
        assert 'error' in response.json()
    
    def test_update_empty_body(self, boxes_endpoint, test_box):
        """Test: Update ohne Daten"""
        response = requests.put(
            f"{boxes_endpoint}/{test_box['code']}",
            json={}
        )
        
        # Sollte einen Fehler zurückgeben
        assert response.status_code == 400


# ========================================
# DELETE TESTS (DELETE)
# ========================================

class TestDeleteBox:
    """Tests für das Löschen von Kisten"""
    
    def test_delete_box(self, boxes_endpoint):
        """Test: Kiste löschen"""
        # Erstelle eine Kiste zum Löschen
        create_response = requests.post(
            boxes_endpoint,
            json={"Location": "Zum Löschen"}
        )
        code = create_response.json()['CODE']
        
        # Lösche die Kiste
        delete_response = requests.delete(f"{boxes_endpoint}/{code}")
        
        assert delete_response.status_code == 204, "Status sollte 204 (No Content) sein"
        
        # Prüfe ob Kiste wirklich gelöscht wurde
        get_response = requests.get(f"{boxes_endpoint}/{code}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_box(self, boxes_endpoint):
        """Test: Nicht existierende Kiste löschen"""
        response = requests.delete(f"{boxes_endpoint}/XXXX")
        
        assert response.status_code == 404
        assert 'error' in response.json()


# ========================================
# REST-PRINZIPIEN TESTS
# ========================================

class TestRESTPrinciples:
    """Tests für REST-Prinzipien"""
    
    def test_statelessness(self, boxes_endpoint, test_box):
        """
        Test: Zustandslosigkeit
        Jeder Request sollte alle notwendigen Informationen enthalten
        """
        # Erste Anfrage
        response1 = requests.get(f"{boxes_endpoint}/{test_box['code']}")
        
        # Zweite Anfrage (Server sollte keine Session-Daten gespeichert haben)
        response2 = requests.get(f"{boxes_endpoint}/{test_box['code']}")
        
        # Beide Antworten sollten identisch sein
        assert response1.json() == response2.json()
    
    def test_content_type_headers(self, boxes_endpoint):
        """Test: Content-Type Header werden korrekt gesetzt"""
        response = requests.get(boxes_endpoint)
        
        assert 'Content-Type' in response.headers
        assert 'application/json' in response.headers['Content-Type']
    
    def test_hateoas_links_consistency(self, boxes_endpoint, test_box):
        """Test: HATEOAS Links sind konsistent und funktionieren"""
        response = requests.get(f"{boxes_endpoint}/{test_box['code']}")
        result = response.json()
        
        # Prüfe ob Links vorhanden sind
        assert '_links' in result
        
        # Teste ob self-Link funktioniert
        self_link = result['_links']['self']['href']
        self_response = requests.get(f"http://localhost:5001{self_link}")
        assert self_response.status_code == 200
        
        # Teste ob collection-Link funktioniert
        collection_link = result['_links']['collection']['href']
        collection_response = requests.get(f"http://localhost:5001{collection_link}")
        assert collection_response.status_code == 200


# ========================================
# RUN TESTS
# ========================================

if __name__ == '__main__':
    print("Starte Tests...")
    print("Stelle sicher, dass der Server läuft auf http://localhost:5001")
    print()
    pytest.main([__file__, '-v'])
