# tests/domains/department/test_department_router.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
class TestDepartmentRouter:
    @pytest.fixture(autouse=True)
    async def setup(self, client: AsyncClient):
        """Fixture to set up any common state before each test."""
        self.client = client

    async def test_create_department(self):
        """Test creating a new department"""
        api_body = {"title": "Test Department", "created_by_id": 1, "process_ids": []}
        response = await self.client.post("/api/v1/departments/", json=api_body)

        # Print the error response if status code is not 201
        if response.status_code != 201:
            print(f"Error response: {response.text}")

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == api_body["title"]
        assert data["created_by"]["id"] == api_body["created_by_id"]

    async def test_read_departments(self):
        """Test retrieving all departments"""
        # First create a department to ensure at least one exists
        create_body = {
            "title": "Department for List Test",
            "created_by_id": 1,
            "process_ids": [],
        }
        await self.client.post("/api/v1/departments/", json=create_body)

        # Test the list endpoint
        response = await self.client.get("/api/v1/departments/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify pagination works
        response_limited = await self.client.get("/api/v1/departments/?limit=1")
        assert response_limited.status_code == 200
        data_limited = response_limited.json()
        assert len(data_limited) <= 1

    async def test_read_department_by_id(self):
        """Test retrieving a specific department by ID"""
        # First create a department to get a valid ID
        create_body = {
            "title": "Department for Get Test",
            "created_by_id": 1,
            "process_ids": [],
        }
        create_response = await self.client.post("/api/v1/departments/", json=create_body)
        created_department = create_response.json()
        department_id = created_department["id"]

        # Test getting by ID
        response = await self.client.get(f"/api/v1/departments/{department_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == department_id
        assert data["title"] == create_body["title"]

    async def test_read_department_not_found(self):
        """Test 404 response when department ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        response = await self.client.get(f"/api/v1/departments/{non_existent_id}")

        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    async def test_update_department(self):
        """Test updating an existing department"""
        # First create a department to update
        create_body = {
            "title": "Original Department Title",
            "created_by_id": 1,
            "process_ids": [],
        }
        create_response = await self.client.post("/api/v1/departments/", json=create_body)
        created_department = create_response.json()
        department_id = created_department["id"]

        # Update the department
        update_body = {
            "title": "Updated Department Title",
            "process_ids": [1],  # Assuming process with ID 1 exists
        }
        response = await self.client.put(f"/api/v1/departments/{department_id}", json=update_body)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == department_id
        assert data["title"] == update_body["title"]
        assert len(data["processes"]) == 1
        assert data["processes"][0]["id"] == update_body["process_ids"][0]

    async def test_delete_department(self):
        """Test deleting a department"""
        # First create a department to delete
        create_body = {
            "title": "Department to Delete",
            "created_by_id": 1,
            "process_ids": [],
        }
        create_response = await self.client.post("/api/v1/departments/", json=create_body)
        created_department = create_response.json()
        department_id = created_department["id"]

        # Delete the department
        delete_response = await self.client.delete(f"/api/v1/departments/{department_id}")

        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert "message" in delete_data
        assert delete_data["message"] == "Department deleted successfully"

        # Verify it's gone by trying to get it
        get_response = await self.client.get(f"/api/v1/departments/{department_id}")
        assert get_response.status_code == 404
