import pytest
from app.domains.process.process_schemas import ProcessCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domains.process.process_dependencies import get_process_service


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
            role_ids=[1]  # Assuming a role with ID 1 exists
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
            role_ids=[1]
        )

        # Check if it raises an HTTPException with appropriate status code
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_process(invalid_process_data)
        
        assert excinfo.value.status_code == 500  # Custom error code for failure
        # Check for foreign key violation in the error message
        assert "ForeignKeyViolationError" in str(excinfo.value.detail)
