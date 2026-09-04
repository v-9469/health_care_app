"""
Pytest Feature Tests: Doctor Management Module (In-Memory Mock DB).
"""
import pytest
from rest_framework import status


class TestDoctorCreation:
    """Tests for POST /api/doctors/"""

    def test_create_doctor_success(self, auth_client, mock_container_dependencies):
        payload = {
            "name": "Gregory House",
            "specialization": "Diagnostic Medicine",
            "contact_number": "+1234567890",
            "email": "house@princetonplainsboro.com",
            "experience_years": 15
        }
        response = auth_client.post("/api/doctors/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "Gregory House"
        assert response.data["data"]["specialization"] == "Diagnostic Medicine"
        assert response.data["data"]["email"] == "house@princetonplainsboro.com"
        assert response.data["data"]["experience_years"] == 15
        assert "id" in response.data["data"]

        # Verify mock repository stored the doctor record
        doctor_repo = mock_container_dependencies["doctor_repo"]
        saved = doctor_repo.get_by_email("house@princetonplainsboro.com")
        assert saved is not None
        assert saved.name == "Gregory House"

    def test_create_doctor_unauthenticated_fails(self, api_client):
        payload = {
            "name": "Allison Cameron",
            "specialization": "Immunology",
            "contact_number": "+1987654321",
            "email": "cameron@hospital.com",
            "experience_years": 5
        }
        response = api_client.post("/api/doctors/", payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_create_doctor_duplicate_email_fails(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        doctor_repo.create(
            name="James Wilson",
            specialization="Oncology",
            contact_number="+1555000111",
            email="wilson@hospital.org",
            experience_years=12
        )

        payload = {
            "name": "James Wilson Clone",
            "specialization": "Oncology",
            "contact_number": "+1555000222",
            "email": "wilson@hospital.org",  # Same email
            "experience_years": 8
        }
        response = auth_client.post("/api/doctors/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "DUPLICATE_RESOURCE"

    def test_create_doctor_invalid_email_fails(self, auth_client):
        payload = {
            "name": "Lisa Cuddy",
            "specialization": "Endocrinology",
            "contact_number": "+1555222333",
            "email": "not-a-valid-email",
            "experience_years": 14
        }
        response = auth_client.post("/api/doctors/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_create_doctor_missing_required_fields_fails(self, auth_client):
        payload = {
            "name": "Robert Chase"
            # Missing specialization, contact_number, email
        }
        response = auth_client.post("/api/doctors/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_create_doctor_negative_experience_fails(self, auth_client):
        payload = {
            "name": "Eric Foreman",
            "specialization": "Neurology",
            "contact_number": "+1555333444",
            "email": "foreman@hospital.org",
            "experience_years": -5  # Negative experience
        }
        response = auth_client.post("/api/doctors/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


class TestDoctorListingAndSearch:
    """Tests for GET /api/doctors/"""

    def test_list_doctors_empty(self, auth_client):
        response = auth_client.get("/api/doctors/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["count"] == 0
        assert response.data["data"] == []

    def test_list_all_doctors(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        doctor_repo.create(name="Dr. Alpha", specialization="Cardiology", contact_number="+111", email="alpha@doc.com", experience_years=5)
        doctor_repo.create(name="Dr. Beta", specialization="Neurology", contact_number="+222", email="beta@doc.com", experience_years=8)
        doctor_repo.create(name="Dr. Gamma", specialization="Cardiology", contact_number="+333", email="gamma@doc.com", experience_years=12)

        response = auth_client.get("/api/doctors/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["count"] == 3
        assert len(response.data["data"]) == 3

    def test_filter_doctors_by_specialization(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        doctor_repo.create(name="Dr. Alpha", specialization="Cardiology", contact_number="+111", email="alpha@doc.com", experience_years=5)
        doctor_repo.create(name="Dr. Beta", specialization="Neurology", contact_number="+222", email="beta@doc.com", experience_years=8)
        doctor_repo.create(name="Dr. Gamma", specialization="Cardiology", contact_number="+333", email="gamma@doc.com", experience_years=12)

        response = auth_client.get("/api/doctors/?specialization=Cardiology")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for doc in response.data["data"]:
            assert doc["specialization"] == "Cardiology"

    def test_search_doctors_by_keyword(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        doctor_repo.create(name="Gregory House", specialization="Diagnostics", contact_number="+111", email="house@doc.com")
        doctor_repo.create(name="James Wilson", specialization="Oncology", contact_number="+222", email="wilson@doc.com")

        response = auth_client.get("/api/doctors/?search=House")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["data"][0]["name"] == "Gregory House"


class TestDoctorDetailAndOperations:
    """Tests for GET / PUT / PATCH / DELETE /api/doctors/<id>/"""

    def test_get_doctor_details_success(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        created = doctor_repo.create(
            name="Meredith Grey",
            specialization="General Surgery",
            contact_number="+1444555666",
            email="grey@seattlegrace.com",
            experience_years=10
        )

        response = auth_client.get(f"/api/doctors/{created.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "Meredith Grey"
        assert response.data["data"]["email"] == "grey@seattlegrace.com"

    def test_get_doctor_nonexistent_fails(self, auth_client):
        response = auth_client.get("/api/doctors/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "NOT_FOUND"

    def test_update_doctor_put_full(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        created = doctor_repo.create(
            name="Cristina Yang",
            specialization="Cardiothoracic Surgery",
            contact_number="+1777888999",
            email="yang@seattlegrace.com",
            experience_years=7
        )

        update_payload = {
            "name": "Dr. Cristina Yang, Chief",
            "specialization": "Cardiothoracic Surgery",
            "contact_number": "+1777888999",
            "email": "yang.chief@seattlegrace.com",
            "experience_years": 9
        }
        response = auth_client.put(f"/api/doctors/{created.id}/", update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "Dr. Cristina Yang, Chief"
        assert response.data["data"]["experience_years"] == 9
        assert response.data["data"]["email"] == "yang.chief@seattlegrace.com"

    def test_update_doctor_patch_partial(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        created = doctor_repo.create(
            name="Derek Shepherd",
            specialization="Neurosurgery",
            contact_number="+1888999000",
            email="shepherd@seattlegrace.com",
            experience_years=16
        )

        patch_payload = {
            "contact_number": "+1999000111",
            "experience_years": 17
        }
        response = auth_client.patch(f"/api/doctors/{created.id}/", patch_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["contact_number"] == "+1999000111"
        assert response.data["data"]["experience_years"] == 17
        assert response.data["data"]["name"] == "Derek Shepherd"  # Unchanged

    def test_delete_doctor_success(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        created = doctor_repo.create(
            name="Alex Karev",
            specialization="Pediatric Surgery",
            contact_number="+1222333444",
            email="karev@seattlegrace.com",
            experience_years=8
        )

        response = auth_client.delete(f"/api/doctors/{created.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Verify doctor was deleted from repository
        assert doctor_repo.get_by_id(created.id) is None

    def test_delete_doctor_nonexistent_fails(self, auth_client):
        response = auth_client.delete("/api/doctors/88888/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
