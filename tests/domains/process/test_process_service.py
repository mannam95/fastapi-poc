import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.process.process_dependencies import get_process_service
from app.domains.process.process_schemas import ProcessCreate, ProcessUpdate


@pytest.mark.asyncio
@pytest.mark.integration
class TestProcessService:
    @pytest.fixture(autouse=True)
    async def setup(self, db_session: AsyncSession):
        """Fixture to set up any common state before each test."""
        self.service = get_process_service(db_session)

    async def test_create_process_integration(self):
        """Test the 'create_process' method"""
        # Prepare mock data
        process_data = ProcessCreate(
            title="Test Process",
            description="This is a test process",
            created_by_id=1,  # Assuming a user with ID 1 exists
            department_ids=[1],  # Assuming a department with ID 1 exists
            location_ids=[1],  # Assuming a location with ID 1 exists
            resource_ids=[1],  # Assuming a resource with ID 1 exists
            role_ids=[1],  # Assuming a role with ID 1 exists
        )

        # Call the create_process method
        created_process = await self.service.create_process(process_data)

        # Assertions
        assert created_process is not None
        assert created_process.title == process_data.title
        assert created_process.description == process_data.description
        assert created_process.created_by_id == process_data.created_by_id
        assert len(created_process.departments) == 1
        assert created_process.departments[0].id == process_data.department_ids[0]
        assert len(created_process.locations) == 1
        assert created_process.locations[0].id == process_data.location_ids[0]
        assert len(created_process.resources) == 1
        assert created_process.resources[0].id == process_data.resource_ids[0]
        assert len(created_process.roles) == 1
        assert created_process.roles[0].id == process_data.role_ids[0]
        assert created_process.id is not None

    async def test_create_process_failure(self):
        """Test failure case for 'create_process' with invalid data"""
        # Simulating an invalid created_by_id (non-existing user)
        invalid_process_data = ProcessCreate(
            title="Invalid Process",
            description="This should fail",
            created_by_id=99999,  # Assuming this user does not exist
            department_ids=[1],
            location_ids=[1],
            resource_ids=[1],
            role_ids=[1],
        )

        # Check if it raises an HTTPException with appropriate status code
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_process(invalid_process_data)

        assert excinfo.value.status_code == 500  # Custom error code for failure
        # Check for foreign key violation in the error message
        assert "ForeignKeyViolationError" in str(excinfo.value.detail)

    async def test_get_processes(self):
        """Test retrieving a list of processes with pagination"""
        # Create a process to ensure we have at least one in the database
        process_data = ProcessCreate(
            title="Process for List Test",
            description="Testing get_processes method",
            created_by_id=1,
            department_ids=[],
            location_ids=[],
            resource_ids=[],
            role_ids=[],
        )
        await self.service.create_process(process_data)

        # Test the get_processes method with default pagination
        processes = await self.service.get_processes()

        # Assertions
        assert isinstance(processes, list)
        assert len(processes) > 0

        # Test pagination with limit
        limited_processes = await self.service.get_processes(limit=1)
        assert len(limited_processes) <= 1

        # Test pagination with offset
        offset_processes = await self.service.get_processes(offset=1, limit=10)
        if len(processes) > 1:
            # If we have more than one process, the first process with offset should differ
            assert offset_processes[0].id != processes[0].id

    async def test_get_process_by_id(self):
        """Test retrieving a single process by ID"""
        # Create a process to get a valid ID
        process_data = ProcessCreate(
            title="Process for Get Test",
            description="Testing get_process_by_id method",
            created_by_id=1,
            department_ids=[1],
            location_ids=[1],
            resource_ids=[],
            role_ids=[],
        )
        created_process = await self.service.create_process(process_data)
        process_id = created_process.id

        # Test getting the process by ID
        retrieved_process = await self.service.get_process_by_id(process_id)

        # Assertions
        assert retrieved_process is not None
        assert retrieved_process.id == process_id
        assert retrieved_process.title == process_data.title
        assert retrieved_process.description == process_data.description
        assert retrieved_process.created_by_id == process_data.created_by_id
        assert len(retrieved_process.departments) == 1
        assert len(retrieved_process.locations) == 1

    async def test_get_process_by_id_not_found(self):
        """Test 404 error when process ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_process_by_id(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_process(self):
        """Test updating an existing process"""
        # Create a process to update
        process_data = ProcessCreate(
            title="Original Process Title",
            description="Original description",
            created_by_id=1,
            department_ids=[],
            location_ids=[],
            resource_ids=[],
            role_ids=[],
        )
        created_process = await self.service.create_process(process_data)
        process_id = created_process.id

        # Update data
        update_data = ProcessUpdate(
            title="Updated Process Title",
            description="Updated description",
            department_ids=[1],  # Assuming department with ID 1 exists
            location_ids=[1],  # Assuming location with ID 1 exists
        )

        # Update the process
        updated_process = await self.service.update_process(process_id, update_data)

        # Assertions
        assert updated_process.id == process_id
        assert updated_process.title == update_data.title
        assert updated_process.description == update_data.description
        assert len(updated_process.departments) == 1
        assert updated_process.departments[0].id == update_data.department_ids[0]
        assert len(updated_process.locations) == 1
        assert updated_process.locations[0].id == update_data.location_ids[0]

        # Original data should be preserved if not included in update
        assert updated_process.created_by_id == process_data.created_by_id

    async def test_update_process_not_found(self):
        """Test update with non-existent process ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        update_data = ProcessUpdate(title="Updated Title")

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_process(non_existent_id, update_data)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_process_invalid_relationships(self):
        """Test update with invalid relationship IDs"""
        # Create a process to update
        process_data = ProcessCreate(
            title="Process for Invalid Update",
            description="Will be updated with invalid data",
            created_by_id=1,
            department_ids=[],
            location_ids=[],
            resource_ids=[],
            role_ids=[],
        )
        created_process = await self.service.create_process(process_data)
        process_id = created_process.id

        # Update with invalid department ID
        invalid_update = ProcessUpdate(
            title="Updated with Invalid Department",
            department_ids=[99999],  # Assuming this department ID doesn't exist
        )

        # Check if it raises an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_process(process_id, invalid_update)

        assert excinfo.value.status_code == 500

    async def test_delete_process(self):
        """Test deleting a process"""
        # Create a process to delete
        process_data = ProcessCreate(
            title="Process to Delete",
            description="This will be deleted",
            created_by_id=1,
            department_ids=[],
            location_ids=[],
            resource_ids=[],
            role_ids=[],
        )
        created_process = await self.service.create_process(process_data)
        process_id = created_process.id

        # Delete the process
        await self.service.delete_process(process_id)

        # Verify it's deleted by trying to get it
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_process_by_id(process_id)

        assert excinfo.value.status_code == 404

    async def test_delete_process_not_found(self):
        """Test delete with non-existent process ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.delete_process(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_delete_process_exception(self):
        """Test that exceptions during process deletion are handled correctly"""
        # Create a process to get a valid ID
        process_data = ProcessCreate(
            title="Process for Exception Test",
            description="Testing exception handling",
            created_by_id=1,
            department_ids=[],
            location_ids=[],
            resource_ids=[],
            role_ids=[],
        )
        created_process = await self.service.create_process(process_data)
        process_id = created_process.id

        # Mock the session's delete method to raise an exception
        original_delete = self.service.session.delete

        async def mock_delete_with_exception(*args, **kwargs):
            raise Exception("Database error during delete")

        # Replace the delete method with our mocked version
        self.service.session.delete = mock_delete_with_exception

        try:
            # The delete operation should now raise an HTTPException
            with pytest.raises(HTTPException) as excinfo:
                await self.service.delete_process(process_id)

            # Verify the exception details
            assert excinfo.value.status_code == 500
            assert "Database error during delete" in str(excinfo.value.detail)
        finally:
            # Restore the original delete method
            self.service.session.delete = original_delete
