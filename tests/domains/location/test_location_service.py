import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.location.location_dependencies import get_location_service
from app.domains.location.location_schemas import LocationCreate, LocationUpdate


@pytest.mark.asyncio
@pytest.mark.integration
class TestLocationService:
    @pytest.fixture(autouse=True)
    async def setup(self, db_session: AsyncSession):
        """Fixture to set up any common state before each test."""
        self.service = get_location_service(db_session)

    async def test_create_location_integration(self):
        """Test the 'create_location' method"""
        # Prepare test data
        location_data = LocationCreate(
            title="Test Location",
            created_by_id=1,  # Assuming a user with ID 1 exists
            process_ids=[1],  # Assuming a process with ID 1 exists
        )

        # Call the create_location method
        created_location = await self.service.create_location(location_data)

        # Assertions
        assert created_location is not None
        assert created_location.title == location_data.title
        assert created_location.created_by_id == location_data.created_by_id
        assert len(created_location.processes) == 1
        assert created_location.processes[0].id == location_data.process_ids[0]
        assert created_location.id is not None

    async def test_create_location_failure(self):
        """Test failure case for 'create_location' with invalid data"""
        # Simulating an invalid created_by_id (non-existing user)
        invalid_location_data = LocationCreate(
            title="Invalid Location",
            created_by_id=99999,  # Assuming this user does not exist
            process_ids=[1],
        )

        # Check if it raises an HTTPException with appropriate status code
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_location(invalid_location_data)

        assert excinfo.value.status_code == 400
        # Foreign key violation should be in the error message
        assert (
            "ForeignKeyViolationError" in str(excinfo.value.detail)
            or "foreign key" in str(excinfo.value.detail).lower()
        )

    async def test_get_locations(self):
        """Test retrieving a list of locations with pagination"""
        # Create a location to ensure we have at least one in the database
        location_data = LocationCreate(
            title="Location for List Test", created_by_id=1, process_ids=[]
        )
        await self.service.create_location(location_data)

        # Test the get_locations method with default pagination
        locations = await self.service.get_locations()

        # Assertions
        assert isinstance(locations, list)
        assert len(locations) > 0

        # Test pagination with limit
        limited_locations = await self.service.get_locations(limit=1)
        assert len(limited_locations) <= 1

        # Test pagination with offset
        offset_locations = await self.service.get_locations(offset=1, limit=10)
        if len(locations) > 1:
            # If we have more than one location, the first location with offset should differ
            assert offset_locations[0].id != locations[0].id

    async def test_get_location_by_id(self):
        """Test retrieving a single location by ID"""
        # Create a location to get a valid ID
        location_data = LocationCreate(
            title="Location for Get Test", created_by_id=1, process_ids=[1]
        )
        created_location = await self.service.create_location(location_data)
        location_id = created_location.id

        # Test getting the location by ID
        retrieved_location = await self.service.get_location_by_id(location_id)

        # Assertions
        assert retrieved_location is not None
        assert retrieved_location.id == location_id
        assert retrieved_location.title == location_data.title
        assert retrieved_location.created_by_id == location_data.created_by_id
        assert len(retrieved_location.processes) == 1

    async def test_get_location_by_id_not_found(self):
        """Test 404 error when location ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_location_by_id(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_location(self):
        """Test updating an existing location"""
        # Create a location to update
        location_data = LocationCreate(
            title="Original Location Title", created_by_id=1, process_ids=[]
        )
        created_location = await self.service.create_location(location_data)
        location_id = created_location.id

        # Update data
        update_data = LocationUpdate(
            title="Updated Location Title",
            process_ids=[1],  # Assuming process with ID 1 exists
        )

        # Update the location
        updated_location = await self.service.update_location(location_id, update_data)

        # Assertions
        assert updated_location.id == location_id
        assert updated_location.title == update_data.title
        assert len(updated_location.processes) == 1
        assert updated_location.processes[0].id == update_data.process_ids[0]

        # Original data should be preserved if not included in update
        assert updated_location.created_by_id == location_data.created_by_id

    async def test_update_location_not_found(self):
        """Test update with non-existent location ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        update_data = LocationUpdate(title="Updated Title")

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_location(non_existent_id, update_data)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_location_invalid_relationships(self):
        """Test update with invalid relationship IDs"""
        # Create a location to update
        location_data = LocationCreate(
            title="Location for Invalid Update", created_by_id=1, process_ids=[]
        )
        created_location = await self.service.create_location(location_data)
        location_id = created_location.id

        # Update with invalid process ID
        invalid_update = LocationUpdate(
            title="Updated with Invalid Process",
            process_ids=[99999],  # Assuming this process ID doesn't exist
        )

        # Check if it raises an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_location(location_id, invalid_update)

        assert excinfo.value.status_code == 400

    async def test_delete_location(self):
        """Test deleting a location"""
        # Create a location to delete
        location_data = LocationCreate(title="Location to Delete", created_by_id=1, process_ids=[])
        created_location = await self.service.create_location(location_data)
        location_id = created_location.id

        # Delete the location
        await self.service.delete_location(location_id)

        # Verify it's deleted by trying to get it
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_location_by_id(location_id)

        assert excinfo.value.status_code == 404

    async def test_delete_location_not_found(self):
        """Test delete with non-existent location ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.delete_location(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()
