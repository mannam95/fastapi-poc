# tests/domains/user/test_user_router.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
class TestUserRouter:
    @pytest.fixture(autouse=True)
    async def setup(self, client: AsyncClient):
        """Fixture to set up any common state before each test."""
        self.client = client

    async def test_create_user(self):
        """Test creating a new user"""
        api_body = {"title": "Test User"}
        response = await self.client.post("/api/v1/users/", json=api_body)

        # Print the error response if status code is not 201
        if response.status_code != 201:
            print(f"Error response: {response.text}")

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == api_body["title"]
        assert "id" in data
        assert "created_at" in data

    async def test_read_users(self):
        """Test retrieving all users"""
        # First create a user to ensure at least one exists
        create_body = {"title": "User for List Test"}
        await self.client.post("/api/v1/users/", json=create_body)

        # Test the list endpoint
        response = await self.client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify pagination works
        response_limited = await self.client.get("/api/v1/users/?limit=1")
        assert response_limited.status_code == 200
        data_limited = response_limited.json()
        assert len(data_limited) <= 1

    async def test_read_user_by_id(self):
        """Test retrieving a specific user by ID"""
        # First create a user to get a valid ID
        create_body = {"title": "User for Get Test"}
        create_response = await self.client.post("/api/v1/users/", json=create_body)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Test getting by ID
        response = await self.client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["title"] == create_body["title"]
        assert "created_at" in data

    async def test_read_user_not_found(self):
        """Test 404 response when user ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        response = await self.client.get(f"/api/v1/users/{non_existent_id}")

        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    async def test_update_user(self):
        """Test updating an existing user"""
        # First create a user to update
        create_body = {"title": "Original User Title"}
        create_response = await self.client.post("/api/v1/users/", json=create_body)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Update the user
        update_body = {"title": "Updated User Title"}
        response = await self.client.put(f"/api/v1/users/{user_id}", json=update_body)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["title"] == update_body["title"]
        assert "created_at" in data

    async def test_delete_user(self):
        """Test deleting a user"""
        # First create a user to delete
        create_body = {"title": "User to Delete"}
        create_response = await self.client.post("/api/v1/users/", json=create_body)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Delete the user
        delete_response = await self.client.delete(f"/api/v1/users/{user_id}")

        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert "message" in delete_data
        assert delete_data["message"] == "User deleted successfully"

        # Verify it's gone by trying to get it
        get_response = await self.client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404
