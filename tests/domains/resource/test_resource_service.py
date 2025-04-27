import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.resource.resource_dependencies import get_resource_service
from app.domains.resource.resource_schemas import ResourceCreate, ResourceUpdate


@pytest.mark.asyncio
@pytest.mark.integration
class TestResourceService:
    @pytest.fixture(autouse=True)
    async def setup(self, db_session: AsyncSession):
        """Fixture to set up any common state before each test."""
        self.service = get_resource_service(db_session)

    async def test_create_resource_integration(self):
        """Test the 'create_resource' method"""
        # Prepare test data
        resource_data = ResourceCreate(
            title="Test Resource",
            created_by_id=1,  # Assuming a user with ID 1 exists
            process_ids=[1],  # Assuming a process with ID 1 exists
        )

        # Call the create_resource method
        created_resource = await self.service.create_resource(resource_data)

        # Assertions
        assert created_resource is not None
        assert created_resource.title == resource_data.title
        assert created_resource.created_by_id == resource_data.created_by_id
        assert len(created_resource.processes) == 1
        assert created_resource.processes[0].id == resource_data.process_ids[0]
        assert created_resource.id is not None

    async def test_create_resource_failure(self):
        """Test failure case for 'create_resource' with invalid data"""
        # Simulating an invalid created_by_id (non-existing user)
        invalid_resource_data = ResourceCreate(
            title="Invalid Resource",
            created_by_id=99999,  # Assuming this user does not exist
            process_ids=[1],
        )

        # Check if it raises an HTTPException with appropriate status code
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_resource(invalid_resource_data)

        assert excinfo.value.status_code == 500
        # Foreign key violation should be in the error message
        assert (
            "ForeignKeyViolationError" in str(excinfo.value.detail)
            or "foreign key" in str(excinfo.value.detail).lower()
        )

    async def test_get_resources(self):
        """Test retrieving a list of resources with pagination"""
        # Create a resource to ensure we have at least one in the database
        resource_data = ResourceCreate(
            title="Resource for List Test", created_by_id=1, process_ids=[]
        )
        await self.service.create_resource(resource_data)

        # Test the get_resources method with default pagination
        resources = await self.service.get_resources()

        # Assertions
        assert isinstance(resources, list)
        assert len(resources) > 0

        # Test pagination with limit
        limited_resources = await self.service.get_resources(limit=1)
        assert len(limited_resources) <= 1

        # Test pagination with offset
        offset_resources = await self.service.get_resources(offset=1, limit=10)
        if len(resources) > 1:
            # If we have more than one resource, the first resource with offset should differ
            assert offset_resources[0].id != resources[0].id

    async def test_get_resource_by_id(self):
        """Test retrieving a single resource by ID"""
        # Create a resource to get a valid ID
        resource_data = ResourceCreate(
            title="Resource for Get Test", created_by_id=1, process_ids=[1]
        )
        created_resource = await self.service.create_resource(resource_data)
        resource_id = created_resource.id

        # Test getting the resource by ID
        retrieved_resource = await self.service.get_resource_by_id(resource_id)

        # Assertions
        assert retrieved_resource is not None
        assert retrieved_resource.id == resource_id
        assert retrieved_resource.title == resource_data.title
        assert retrieved_resource.created_by_id == resource_data.created_by_id
        assert len(retrieved_resource.processes) == 1

    async def test_get_resource_by_id_not_found(self):
        """Test 404 error when resource ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_resource_by_id(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_resource(self):
        """Test updating an existing resource"""
        # Create a resource to update
        resource_data = ResourceCreate(
            title="Original Resource Title", created_by_id=1, process_ids=[]
        )
        created_resource = await self.service.create_resource(resource_data)
        resource_id = created_resource.id

        # Update data
        update_data = ResourceUpdate(
            title="Updated Resource Title",
            process_ids=[1],  # Assuming process with ID 1 exists
        )

        # Update the resource
        updated_resource = await self.service.update_resource(resource_id, update_data)

        # Assertions
        assert updated_resource.id == resource_id
        assert updated_resource.title == update_data.title
        assert len(updated_resource.processes) == 1
        assert updated_resource.processes[0].id == update_data.process_ids[0]

        # Original data should be preserved if not included in update
        assert updated_resource.created_by_id == resource_data.created_by_id

    async def test_update_resource_not_found(self):
        """Test update with non-existent resource ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        update_data = ResourceUpdate(title="Updated Title")

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_resource(non_existent_id, update_data)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_resource_invalid_relationships(self):
        """Test update with invalid relationship IDs"""
        # Create a resource to update
        resource_data = ResourceCreate(
            title="Resource for Invalid Update", created_by_id=1, process_ids=[]
        )
        created_resource = await self.service.create_resource(resource_data)
        resource_id = created_resource.id

        # Update with invalid process ID
        invalid_update = ResourceUpdate(
            title="Updated with Invalid Process",
            process_ids=[99999],  # Assuming this process ID doesn't exist
        )

        # Check if it raises an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_resource(resource_id, invalid_update)

        assert excinfo.value.status_code == 500

    async def test_delete_resource(self):
        """Test deleting a resource"""
        # Create a resource to delete
        resource_data = ResourceCreate(title="Resource to Delete", created_by_id=1, process_ids=[])
        created_resource = await self.service.create_resource(resource_data)
        resource_id = created_resource.id

        # Delete the resource
        await self.service.delete_resource(resource_id)

        # Verify it's deleted by trying to get it
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_resource_by_id(resource_id)

        assert excinfo.value.status_code == 404

    async def test_delete_resource_not_found(self):
        """Test delete with non-existent resource ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.delete_resource(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_delete_resource_exception(self):
        """Test that exceptions during resource deletion are handled correctly"""
        # Create a resource to get a valid ID
        resource_data = ResourceCreate(
            title="Resource for Exception Test", created_by_id=1, process_ids=[]
        )
        created_resource = await self.service.create_resource(resource_data)
        resource_id = created_resource.id

        # Mock the session's delete method to raise an exception
        original_delete = self.service.session.delete

        async def mock_delete_with_exception(*args, **kwargs):
            raise Exception("Database error during delete")

        # Replace the delete method with our mocked version
        self.service.session.delete = mock_delete_with_exception

        try:
            # The delete operation should now raise an HTTPException
            with pytest.raises(HTTPException) as excinfo:
                await self.service.delete_resource(resource_id)

            # Verify the exception details
            assert excinfo.value.status_code == 500
            assert "Database error during delete" in str(excinfo.value.detail)
        finally:
            # Restore the original delete method
            self.service.session.delete = original_delete
