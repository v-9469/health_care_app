"""
Pytest Feature Tests: Patient-Doctor Mapping Module (In-Memory Mock DB).
"""
import pytest
from rest_framework import status


class TestMappingCreation:
    """Tests for POST /api/mappings/ (Assigning doctors to patients)"""

    def test_assign_doctor_success(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]

        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Sherlock Holmes",
            age=38,
            gender="Male",
            contact_number="+4412345678",
            address="221B Baker St"
        )
        doctor = doctor_repo.create(
            name="Dr. John Watson",
            specialization="General Medicine",
            contact_number="+4487654321",
            email="watson@bakerstreet.com",
            experience_years=12
        )

        payload = {
            "patient_id": patient.id,
            "doctor_id": doctor.id,
            "notes": "Primary physician assigned for regular consultation."
        }
        response = auth_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["patient_id"] == patient.id
        assert response.data["data"]["doctor_id"] == doctor.id
        assert response.data["data"]["notes"] == "Primary physician assigned for regular consultation."
        assert response.data["data"]["patient"]["name"] == "Sherlock Holmes"
        assert response.data["data"]["doctor"]["name"] == "Dr. John Watson"

        # Verify mapping is in repository
        mapping_repo = mock_container_dependencies["mapping_repo"]
        assert mapping_repo.exists(patient.id, doctor.id) is True

    def test_assign_doctor_unauthenticated_fails(self, api_client):
        payload = {
            "patient_id": 1,
            "doctor_id": 1,
            "notes": "Unauthenticated test"
        }
        response = api_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_assign_doctor_nonexistent_patient_fails(self, auth_client, mock_container_dependencies):
        doctor_repo = mock_container_dependencies["doctor_repo"]
        doctor = doctor_repo.create(
            name="Dr. Gregory House",
            specialization="Diagnostics",
            contact_number="+1000",
            email="house@princeton.org"
        )

        payload = {
            "patient_id": 99999,  # Non-existent patient
            "doctor_id": doctor.id
        }
        response = auth_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "NOT_FOUND"

    def test_assign_doctor_nonexistent_doctor_fails(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="James Wilson",
            age=42,
            gender="Male",
            contact_number="+1001",
            address="Plainsboro"
        )

        payload = {
            "patient_id": patient.id,
            "doctor_id": 88888  # Non-existent doctor
        }
        response = auth_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "NOT_FOUND"

    def test_assign_doctor_unauthorized_other_user_patient_fails(
        self, auth_user, second_client, second_user, mock_container_dependencies
    ):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]

        # Patient created by User A
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="User A Patient",
            age=30,
            gender="Female",
            contact_number="+1002",
            address="Street A"
        )
        doctor = doctor_repo.create(
            name="Dr. Robert Chase",
            specialization="Intensive Care",
            contact_number="+1003",
            email="chase@princeton.org"
        )

        # User B attempts to assign doctor to User A's patient
        payload = {
            "patient_id": patient.id,
            "doctor_id": doctor.id
        }
        response = second_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False

    def test_assign_doctor_duplicate_fails(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]
        mapping_repo = mock_container_dependencies["mapping_repo"]

        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Lisa Cuddy",
            age=40,
            gender="Female",
            contact_number="+1004",
            address="Dean Office"
        )
        doctor = doctor_repo.create(
            name="Dr. Allison Cameron",
            specialization="Immunology",
            contact_number="+1005",
            email="cameron@princeton.org"
        )

        # First assignment
        mapping_repo.assign(patient_id=patient.id, doctor_id=doctor.id, patient=patient, doctor=doctor)

        # Second assignment attempt via API
        payload = {
            "patient_id": patient.id,
            "doctor_id": doctor.id
        }
        response = auth_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "DUPLICATE_RESOURCE"

    def test_assign_doctor_missing_fields_fails(self, auth_client):
        payload = {"notes": "Missing patient and doctor"}
        response = auth_client.post("/api/mappings/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


class TestMappingListingAndIsolation:
    """Tests for GET /api/mappings/ and GET /api/mappings/<patient_id>/"""

    def test_list_mappings_empty(self, auth_client):
        response = auth_client.get("/api/mappings/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["count"] == 0
        assert response.data["data"] == []

    def test_list_mappings_user_isolation(
        self, auth_client, auth_user, second_client, second_user, mock_container_dependencies
    ):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]
        mapping_repo = mock_container_dependencies["mapping_repo"]

        doctor1 = doctor_repo.create(name="Doctor One", specialization="Neurology", contact_number="+11", email="doc1@h.org")
        doctor2 = doctor_repo.create(name="Doctor Two", specialization="Cardiology", contact_number="+22", email="doc2@h.org")

        # Patient for User A
        patient_a = patient_repo.create(user_id=auth_user.id, name="Patient A", age=25, gender="Male", contact_number="+1", address="Add A")
        mapping_repo.assign(patient_id=patient_a.id, doctor_id=doctor1.id, patient=patient_a, doctor=doctor1)

        # Patient for User B
        patient_b = patient_repo.create(user_id=second_user.id, name="Patient B", age=35, gender="Female", contact_number="+2", address="Add B")
        mapping_repo.assign(patient_id=patient_b.id, doctor_id=doctor2.id, patient=patient_b, doctor=doctor2)

        # User A listing mappings
        response_a = auth_client.get("/api/mappings/")
        assert response_a.status_code == status.HTTP_200_OK
        assert response_a.data["count"] == 1
        assert response_a.data["data"][0]["patient_id"] == patient_a.id

        # User B listing mappings
        response_b = second_client.get("/api/mappings/")
        assert response_b.status_code == status.HTTP_200_OK
        assert response_b.data["count"] == 1
        assert response_b.data["data"][0]["patient_id"] == patient_b.id

    def test_get_doctors_assigned_to_patient_success(
        self, auth_client, auth_user, mock_container_dependencies
    ):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]
        mapping_repo = mock_container_dependencies["mapping_repo"]

        patient = patient_repo.create(user_id=auth_user.id, name="Patient Multi-Doc", age=45, gender="Male", contact_number="+3", address="Add Multi")
        doc1 = doctor_repo.create(name="Doc Cardiologist", specialization="Cardiology", contact_number="+31", email="cardio@h.org")
        doc2 = doctor_repo.create(name="Doc Nephrologist", specialization="Nephrology", contact_number="+32", email="nephro@h.org")

        mapping_repo.assign(patient_id=patient.id, doctor_id=doc1.id, patient=patient, doctor=doc1)
        mapping_repo.assign(patient_id=patient.id, doctor_id=doc2.id, patient=patient, doctor=doc2)

        response = auth_client.get(f"/api/mappings/{patient.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["count"] == 2
        assigned_doc_names = [m["doctor"]["name"] for m in response.data["data"]]
        assert "Doc Cardiologist" in assigned_doc_names
        assert "Doc Nephrologist" in assigned_doc_names

    def test_get_doctors_assigned_to_other_user_patient_fails(
        self, auth_user, second_client, mock_container_dependencies
    ):
        patient_repo = mock_container_dependencies["patient_repo"]
        patient = patient_repo.create(
            user_id=auth_user.id,
            name="Private Patient A",
            age=50,
            gender="Male",
            contact_number="+4",
            address="Secret"
        )

        response = second_client.get(f"/api/mappings/{patient.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False

    def test_get_doctors_nonexistent_patient_fails(self, auth_client):
        response = auth_client.get("/api/mappings/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False


class TestMappingDeletion:
    """Tests for DELETE /api/mappings/<id>/ (Unassigning doctor)"""

    def test_delete_mapping_success(self, auth_client, auth_user, mock_container_dependencies):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]
        mapping_repo = mock_container_dependencies["mapping_repo"]

        patient = patient_repo.create(user_id=auth_user.id, name="Patient To Unassign", age=33, gender="Male", contact_number="+5", address="Add")
        doctor = doctor_repo.create(name="Doc To Unassign", specialization="Dermatology", contact_number="+51", email="derm@h.org")
        mapping = mapping_repo.assign(patient_id=patient.id, doctor_id=doctor.id, patient=patient, doctor=doctor)

        response = auth_client.delete(f"/api/mappings/{mapping.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert mapping_repo.get_by_id(mapping.id) is None
        assert mapping_repo.exists(patient.id, doctor.id) is False

    def test_delete_mapping_other_user_patient_forbidden(
        self, auth_user, second_client, mock_container_dependencies
    ):
        patient_repo = mock_container_dependencies["patient_repo"]
        doctor_repo = mock_container_dependencies["doctor_repo"]
        mapping_repo = mock_container_dependencies["mapping_repo"]

        # Mapping belongs to User A's patient
        patient = patient_repo.create(user_id=auth_user.id, name="User A Patient", age=30, gender="Female", contact_number="+6", address="Add")
        doctor = doctor_repo.create(name="Doc Shared", specialization="Orthopedics", contact_number="+61", email="ortho@h.org")
        mapping = mapping_repo.assign(patient_id=patient.id, doctor_id=doctor.id, patient=patient, doctor=doctor)

        # User B attempts to delete User A's mapping
        response = second_client.delete(f"/api/mappings/{mapping.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        # Verify mapping was NOT deleted
        assert mapping_repo.get_by_id(mapping.id) is not None

    def test_delete_nonexistent_mapping_fails(self, auth_client):
        response = auth_client.delete("/api/mappings/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
