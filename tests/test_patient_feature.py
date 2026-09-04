"""
Pytest Feature Tests: Patient Management Module (In-Memory Mock DB).
"""
import pytest
from rest_framework import status


class TestPatientCreation:
    """Tests for POST /api/patients/"""

    def test_create_patient_success(self, auth_client, auth_user, mock_container_dependencies):
        payload = {
            "name": "Arthur Conan Doyle",
            "age": 45,
            "gender": "Male",
            "contact_number": "+1234567890",
            "email": "arthur@doyle.org",
            "address": "221B Baker Street, London",
            "medical_history": "Mild hypertension, non-smoker."
        }
        response = auth_client.post("/api/patients/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "Arthur Conan Doyle"
        assert response.data["data"]["age"] == 45
        assert response.data["data"]["gender"] == "Male"
        assert response.data["data"]["created_by_id"] == auth_user.id
        assert "id" in response.data["data"]

        # Verify mock repository stored the patient record scoped to auth_user
        patient_repo = mock_container_dependencies["patient_repo"]
        saved = patient_repo.get_by_id(response.data["data"]["id"], user_id=auth_user.id)
        assert saved is not None
        assert saved.name == "Arthur Conan Doyle"
        assert saved.created_by_id == auth_user.id

    def test_create_patient_unauthenticated_fails(self, api_client):
        payload = {
            "name": "Anonymous Patient",
            "age": 30,
            "gender": "Female",
            "contact_number": "+1987654321",
            "address": "Unknown Road"
        }
        response = api_client.post("/api/patients/", payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_create_patient_invalid_age_fails(self, auth_client):
        payload = {
            "name": "Invalid Age Patient",
            "age": -10,  # Invalid negative age
            "gender": "Male",
            "contact_number": "+1234567890",
            "address": "123 Main St"
        }
        response = auth_client.post("/api/patients/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_create_patient_invalid_gender_fails(self, auth_client):
        payload = {
            "name": "Invalid Gender Patient",
            "age": 25,
            "gender": "Alien",  # Invalid choice
            "contact_number": "+1234567890",
            "address": "123 Main St"
        }
        response = auth_client.post("/api/patients/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_create_patient_missing_address_fails(self, auth_client):
        payload = {
            "name": "No Address Patient",
            "age": 28,
            "gender": "Female",
            "contact_number": "+1234567890"
            # Missing address
        }
        response = auth_client.post("/api/patients/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


class TestPatientListingAndIsolation:
    """Tests for GET /api/patients/ (Multi-Tenant Scoping)"""

    def test_list_patients_empty(self, auth_client):
        response = auth_client.get("/api/patients/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["count"] == 0
        assert response.data["data"] == []

    def test_list_patients_user_isolation(self, auth_client, auth_user, second_client, second_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]

        # Create 2 patients for User A
        patient_repo.create(user_id=auth_user.id, name="User A Patient 1", age=30, gender="Male", contact_number="+111", address="Address A1")
        patient_repo.create(user_id=auth_user.id, name="User A Patient 2", age=40, gender="Female", contact_number="+222", address="Address A2")

        # Create 1 patient for User B
        patient_repo.create(user_id=second_user.id, name="User B Patient 1", age=50, gender="Other", contact_number="+333", address="Address B1")

        # User A requests their patients
        response_a = auth_client.get("/api/patients/")
        assert response_a.status_code == status.HTTP_200_OK
        assert response_a.data["count"] == 2
        for patient in response_a.data["data"]:
            assert patient["created_by_id"] == auth_user.id
            assert "User A" in patient["name"]

        # User B requests their patients
        response_b = second_client.get("/api/patients/")
        assert response_b.status_code == status.HTTP_200_OK
        assert response_b.data["count"] == 1
        assert response_b.data["data"][0]["created_by_id"] == second_user.id
        assert response_b.data["data"][0]["name"] == "User B Patient 1"

    def test_search_patients_by_name(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient_repo.create(user_id=auth_user.id, name="John Silver", age=35, gender="Male", contact_number="+111", address="Ship A")
        patient_repo.create(user_id=auth_user.id, name="Jim Hawkins", age=16, gender="Male", contact_number="+222", address="Inn B")

        response = auth_client.get("/api/patients/?search=Silver")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["data"][0]["name"] == "John Silver"


class TestPatientDetailAndOperations:
    """Tests for GET / PUT / PATCH / DELETE /api/patients/<id>/"""

    def test_get_patient_details_owner_success(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Irene Adler",
            age=32,
            gender="Female",
            contact_number="+1555444333",
            email="irene@bohemia.com",
            address="Briony Lodge, Serpentine Ave",
            medical_history="None"
        )

        response = auth_client.get(f"/api/patients/{patient.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "Irene Adler"
        assert response.data["data"]["email"] == "irene@bohemia.com"

    def test_get_patient_details_forbidden_other_user(self, auth_user, second_client, second_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        # Patient belongs to User A
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Private Patient",
            age=60,
            gender="Male",
            contact_number="+100",
            address="Secret St"
        )

        # User B attempts to access User A's patient
        response = second_client.get(f"/api/patients/{patient.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "NOT_FOUND"

    def test_get_patient_nonexistent_fails(self, auth_client):
        response = auth_client.get("/api/patients/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False

    def test_update_patient_put_full(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Mycroft Holmes",
            age=50,
            gender="Male",
            contact_number="+1777000111",
            address="Diogenes Club, Pall Mall"
        )

        update_payload = {
            "name": "Mycroft Holmes, Senior",
            "age": 51,
            "gender": "Male",
            "contact_number": "+1777000222",
            "email": "mycroft@diogenes.gov",
            "address": "Diogenes Club, London",
            "medical_history": "Sedentary lifestyle."
        }
        response = auth_client.put(f"/api/patients/{patient.id}/", update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "Mycroft Holmes, Senior"
        assert response.data["data"]["age"] == 51
        assert response.data["data"]["contact_number"] == "+1777000222"

    def test_update_patient_patch_partial(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Mary Morstan",
            age=27,
            gender="Female",
            contact_number="+1888111222",
            address="Forest Hill"
        )

        patch_payload = {
            "contact_number": "+1888999000",
            "address": "Baker Street"
        }
        response = auth_client.patch(f"/api/patients/{patient.id}/", patch_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["contact_number"] == "+1888999000"
        assert response.data["data"]["address"] == "Baker Street"
        assert response.data["data"]["name"] == "Mary Morstan"  # Unchanged

    def test_update_patient_forbidden_other_user(self, auth_user, second_client, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Untouchable Patient",
            age=40,
            gender="Female",
            contact_number="+111",
            address="Lockdown Ave"
        )

        update_payload = {"name": "Hacked Name"}
        response = second_client.patch(f"/api/patients/{patient.id}/", update_payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False

    def test_delete_patient_owner_success(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Toby the Dog",
            age=6,
            gender="Other",
            contact_number="+1999",
            address="Pinchin Lane"
        )

        response = auth_client.delete(f"/api/patients/{patient.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert patient_repo.get_by_id(patient.id, user_id=auth_user.id) is None

    def test_delete_patient_forbidden_other_user(self, auth_user, second_client, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="User A Patient",
            age=22,
            gender="Male",
            contact_number="+111",
            address="Protected St"
        )

        response = second_client.delete(f"/api/patients/{patient.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Verify record still exists
        assert patient_repo.get_by_id(patient.id, user_id=auth_user.id) is not None
