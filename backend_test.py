import requests
import json
from datetime import datetime, timedelta
import time
import os

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

API_URL = f"{BACKEND_URL}/api"
print(f"Testing backend API at: {API_URL}")

# Test data
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

TEST_VEHICLE = {
    "marque": "Renault",
    "modele": "Master",
    "immatriculation": "AB-123-CD",
    "type_vehicule": "camionnette",
    "proprietaire": "ABOU GENI",
    "annee": 2022
}

TEST_DOCUMENT = {
    "type_document": "assurance",
    "numero_document": "ASS-001",
    "date_emission": "2024-01-01T00:00:00.000Z",
    "date_expiration": "2025-01-01T00:00:00.000Z"
}

# Helper functions
def print_test_header(test_name):
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 80}")

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# Test functions
def test_setup():
    print_test_header("Setup Default Admin User")
    response = requests.post(f"{API_URL}/setup")
    print_response(response)
    assert response.status_code in [200, 201], "Setup failed"
    return response.json()

def test_login():
    print_test_header("Authentication - Login")
    response = requests.post(
        f"{API_URL}/auth/login",
        json=TEST_USER
    )
    print_response(response)
    assert response.status_code == 200, "Login failed"
    assert "access_token" in response.json(), "No access token in response"
    return response.json()["access_token"]

def test_unauthorized_access():
    print_test_header("Unauthorized Access Test")
    response = requests.get(f"{API_URL}/vehicles")
    print_response(response)
    assert response.status_code in [401, 403], "Unauthorized access should be rejected"

def test_create_vehicle(token):
    print_test_header("Create Vehicle")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/vehicles",
        json=TEST_VEHICLE,
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Vehicle creation failed"
    return response.json()["id"]

def test_get_vehicles(token):
    print_test_header("Get All Vehicles")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/vehicles",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Get vehicles failed"
    assert isinstance(response.json(), list), "Response should be a list"
    return response.json()

def test_get_vehicle(token, vehicle_id):
    print_test_header(f"Get Vehicle by ID: {vehicle_id}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/vehicles/{vehicle_id}",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Get vehicle by ID failed"
    assert response.json()["id"] == vehicle_id, "Vehicle ID mismatch"
    return response.json()

def test_update_vehicle(token, vehicle_id):
    print_test_header(f"Update Vehicle: {vehicle_id}")
    headers = {"Authorization": f"Bearer {token}"}
    updated_data = TEST_VEHICLE.copy()
    updated_data["modele"] = "Master Updated"
    response = requests.put(
        f"{API_URL}/vehicles/{vehicle_id}",
        json=updated_data,
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Update vehicle failed"
    assert response.json()["modele"] == "Master Updated", "Vehicle update didn't apply"
    return response.json()

def test_create_document(token, vehicle_id):
    print_test_header("Create Document")
    headers = {"Authorization": f"Bearer {token}"}
    document_data = TEST_DOCUMENT.copy()
    document_data["vehicle_id"] = vehicle_id
    response = requests.post(
        f"{API_URL}/documents",
        json=document_data,
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Document creation failed"
    return response.json()["id"]

def test_get_documents(token, vehicle_id=None):
    print_test_header("Get All Documents")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}/documents"
    if vehicle_id:
        url += f"?vehicle_id={vehicle_id}"
    response = requests.get(
        url,
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Get documents failed"
    assert isinstance(response.json(), list), "Response should be a list"
    return response.json()

def test_get_document(token, document_id):
    print_test_header(f"Get Document by ID: {document_id}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/documents/{document_id}",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Get document by ID failed"
    assert response.json()["id"] == document_id, "Document ID mismatch"
    return response.json()

def test_update_document(token, document_id, vehicle_id):
    print_test_header(f"Update Document: {document_id}")
    headers = {"Authorization": f"Bearer {token}"}
    document_data = TEST_DOCUMENT.copy()
    document_data["vehicle_id"] = vehicle_id
    document_data["numero_document"] = "ASS-001-UPDATED"
    response = requests.put(
        f"{API_URL}/documents/{document_id}",
        json=document_data,
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Update document failed"
    assert response.json()["numero_document"] == "ASS-001-UPDATED", "Document update didn't apply"
    return response.json()

def test_get_alerts(token):
    print_test_header("Get Alerts")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/alerts",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Get alerts failed"
    assert isinstance(response.json(), list), "Response should be a list"
    return response.json()

def test_dismiss_alert(token, alert_id):
    print_test_header(f"Dismiss Alert: {alert_id}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{API_URL}/alerts/{alert_id}/dismiss",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Dismiss alert failed"
    return response.json()

def test_statistics(token):
    print_test_header("Get Statistics")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/statistics",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Get statistics failed"
    assert "vehicles_count" in response.json(), "Statistics missing vehicles_count"
    assert "documents_count" in response.json(), "Statistics missing documents_count"
    assert "alerts_count" in response.json(), "Statistics missing alerts_count"
    return response.json()

def test_search(token, query):
    print_test_header(f"Search: {query}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/search?q={query}",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Search failed"
    assert "vehicles" in response.json(), "Search response missing vehicles"
    assert "documents" in response.json(), "Search response missing documents"
    return response.json()

def test_delete_document(token, document_id):
    print_test_header(f"Delete Document: {document_id}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{API_URL}/documents/{document_id}",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Delete document failed"
    return response.json()

def test_delete_vehicle(token, vehicle_id):
    print_test_header(f"Delete Vehicle: {vehicle_id}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{API_URL}/vehicles/{vehicle_id}",
        headers=headers
    )
    print_response(response)
    assert response.status_code == 200, "Delete vehicle failed"
    return response.json()

# Run all tests
def run_all_tests():
    try:
        # Setup and authentication
        test_setup()
        token = test_login()
        test_unauthorized_access()
        
        # Vehicle tests
        vehicle_id = test_create_vehicle(token)
        vehicles = test_get_vehicles(token)
        vehicle = test_get_vehicle(token, vehicle_id)
        updated_vehicle = test_update_vehicle(token, vehicle_id)
        
        # Document tests
        document_id = test_create_document(token, vehicle_id)
        documents = test_get_documents(token)
        documents_for_vehicle = test_get_documents(token, vehicle_id)
        document = test_get_document(token, document_id)
        updated_document = test_update_document(token, document_id, vehicle_id)
        
        # Alert tests
        alerts = test_get_alerts(token)
        if alerts:
            test_dismiss_alert(token, alerts[0]["id"])
        
        # Statistics and search
        stats = test_statistics(token)
        search_results = test_search(token, "Renault")
        
        # Cleanup
        test_delete_document(token, document_id)
        test_delete_vehicle(token, vehicle_id)
        
        print("\n\n✅ All tests completed successfully!")
        return True
    except AssertionError as e:
        print(f"\n\n❌ Test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n\n❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    run_all_tests()