# tests/domains/role/test_role_router.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
class TestRoleRouter:
    @pytest.fixture(autouse=True)
    async def setup(self, client: AsyncClient):
        """Fixture to set up any common state before each test."""
        self.client = client

    async def test_create_role(self):
        """Test creating a new role"""
        api_body = {"title": "Test Role", "created_by_id": 1, "process_ids": []}
        response = await self.client.post("/api/v1/roles/", json=api_body)

        # Print the error response if status code is not 201
        if response.status_code != 201:
            print(f"Error response: {response.text}")

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == api_body["title"]
        assert data["created_by"]["id"] == api_body["created_by_id"]

    async def test_read_roles(self):
        """Test retrieving all roles"""
        # First create a role to ensure at least one exists
        create_body = {
            "title": "Role for List Test",
            "created_by_id": 1,
            "process_ids": [],
        }
        await self.client.post("/api/v1/roles/", json=create_body)

        # Test the list endpoint
        response = await self.client.get("/api/v1/roles/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify pagination works
        response_limited = await self.client.get("/api/v1/roles/?limit=1")
        assert response_limited.status_code == 200
        data_limited = response_limited.json()
        assert len(data_limited) <= 1

    async def test_read_role_by_id(self):
        """Test retrieving a specific role by ID"""
        # First create a role to get a valid ID
        create_body = {
            "title": "Role for Get Test",
            "created_by_id": 1,
            "process_ids": [],
        }
        create_response = await self.client.post("/api/v1/roles/", json=create_body)
        created_role = create_response.json()
        role_id = created_role["id"]

        # Test getting by ID
        response = await self.client.get(f"/api/v1/roles/{role_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == role_id
        assert data["title"] == create_body["title"]

    async def test_read_role_not_found(self):
        """Test 404 response when role ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        response = await self.client.get(f"/api/v1/roles/{non_existent_id}")

        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    async def test_update_role(self):
        """Test updating an existing role"""
        # First create a role to update
        create_body = {
            "title": "Original Role Title",
            "created_by_id": 1,
            "process_ids": [],
        }
        create_response = await self.client.post("/api/v1/roles/", json=create_body)
        created_role = create_response.json()
        role_id = created_role["id"]

        # Update the role
        update_body = {
            "title": "Updated Role Title",
            "process_ids": [1],  # Assuming process with ID 1 exists
        }
        response = await self.client.put(f"/api/v1/roles/{role_id}", json=update_body)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == role_id
        assert data["title"] == update_body["title"]
        assert len(data["processes"]) == 1
        assert data["processes"][0]["id"] == update_body["process_ids"][0]

    async def test_delete_role(self):
        """Test deleting a role"""
        # First create a role to delete
        create_body = {"title": "Role to Delete", "created_by_id": 1, "process_ids": []}
        create_response = await self.client.post("/api/v1/roles/", json=create_body)
        created_role = create_response.json()
        role_id = created_role["id"]

        # Delete the role
        delete_response = await self.client.delete(f"/api/v1/roles/{role_id}")

        assert delete_response.status_code == 204

        # Verify it's gone by trying to get it
        get_response = await self.client.get(f"/api/v1/roles/{role_id}")
        assert get_response.status_code == 404
