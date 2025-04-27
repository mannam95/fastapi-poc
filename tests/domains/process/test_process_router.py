# tests/process/test_process_router.py

import pytest

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_new_process(client):
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
    response = await client.post(
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