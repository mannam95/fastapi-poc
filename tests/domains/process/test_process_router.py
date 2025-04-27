# tests/process/test_process_router.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
@pytest.mark.integration
class TestProcessRouter:
    @pytest.fixture(autouse=True)
    async def setup(self, client: AsyncClient):
        """Fixture to set up any common state before each test."""
        self.client = client

    async def test_create_new_process(self):
        api_body = {
                "title": "Test Process",
                "description": "Testing creation",
                "created_by_id": 1,
                "department_ids": [],
                "location_ids": [],
                "resource_ids": [],
                "role_ids": [],
                "resource_ids": []
            }
        response = await self.client.post(
            "/api/v1/processes/",
            json=api_body
        )
        
        # Print the error response if status code is not 201
        if response.status_code != 201:
            print(f"Error response: {response.text}")
            
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == api_body["title"]
        assert data["description"] == api_body["description"]
        assert data["created_by"]["id"] == api_body["created_by_id"]
    
    async def test_read_processes(self):
        """Test retrieving all processes"""
        # First create a process to ensure at least one exists
        create_body = {
            "title": "Process for List Test",
            "description": "Testing list endpoint",
            "created_by_id": 1,
            "department_ids": [],
            "location_ids": [],
            "resource_ids": [],
            "role_ids": []
        }
        await self.client.post("/api/v1/processes/", json=create_body)
        
        # Test the list endpoint
        response = await self.client.get("/api/v1/processes/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify pagination works
        response_limited = await self.client.get("/api/v1/processes/?limit=1")
        assert response_limited.status_code == 200
        data_limited = response_limited.json()
        assert len(data_limited) <= 1
    
    async def test_read_process_by_id(self):
        """Test retrieving a specific process by ID"""
        # First create a process to get a valid ID
        create_body = {
            "title": "Process for Get Test",
            "description": "Testing get by ID endpoint",
            "created_by_id": 1,
            "department_ids": [],
            "location_ids": [],
            "resource_ids": [],
            "role_ids": []
        }
        create_response = await self.client.post("/api/v1/processes/", json=create_body)
        created_process = create_response.json()
        process_id = created_process["id"]
        
        # Test getting by ID
        response = await self.client.get(f"/api/v1/processes/{process_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == process_id
        assert data["title"] == create_body["title"]
        assert data["description"] == create_body["description"]
    
    async def test_read_process_not_found(self):
        """Test 404 response when process ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        
        response = await self.client.get(f"/api/v1/processes/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
    
    async def test_update_process(self):
        """Test updating an existing process"""
        # First create a process to update
        create_body = {
            "title": "Original Process Title",
            "description": "Original description",
            "created_by_id": 1,
            "department_ids": [],
            "location_ids": [],
            "resource_ids": [],
            "role_ids": []
        }
        create_response = await self.client.post("/api/v1/processes/", json=create_body)
        created_process = create_response.json()
        process_id = created_process["id"]
        
        # Update the process
        update_body = {
            "title": "Updated Process Title",
            "description": "Updated description",
            "department_ids": [1],  # Assuming department with ID 1 exists
            "location_ids": [1]     # Assuming location with ID 1 exists
        }
        response = await self.client.put(
            f"/api/v1/processes/{process_id}",
            json=update_body
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == process_id
        assert data["title"] == update_body["title"]
        assert data["description"] == update_body["description"]
        assert len(data["departments"]) == 1
        assert data["departments"][0]["id"] == update_body["department_ids"][0]
        assert len(data["locations"]) == 1
        assert data["locations"][0]["id"] == update_body["location_ids"][0]
    
    async def test_delete_process(self):
        """Test deleting a process"""
        # First create a process to delete
        create_body = {
            "title": "Process to Delete",
            "description": "This will be deleted",
            "created_by_id": 1,
            "department_ids": [],
            "location_ids": [],
            "resource_ids": [],
            "role_ids": []
        }
        create_response = await self.client.post("/api/v1/processes/", json=create_body)
        created_process = create_response.json()
        process_id = created_process["id"]
        
        # Delete the process
        delete_response = await self.client.delete(f"/api/v1/processes/{process_id}")
        
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert "message" in delete_data
        assert "deleted successfully" in delete_data["message"].lower()
        
        # Verify it's gone by trying to get it
        get_response = await self.client.get(f"/api/v1/processes/{process_id}")
        assert get_response.status_code == 404