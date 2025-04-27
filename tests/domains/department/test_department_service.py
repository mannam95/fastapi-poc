import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.department.department_dependencies import get_department_service
from app.domains.department.department_schemas import DepartmentCreate, DepartmentUpdate


@pytest.mark.asyncio
@pytest.mark.integration
class TestDepartmentService:
    @pytest.fixture(autouse=True)
    async def setup(self, db_session: AsyncSession):
        """Fixture to set up any common state before each test."""
        self.service = get_department_service(db_session)

    async def test_create_department_integration(self):
        """Test the 'create_department' method"""
        # Prepare test data
        department_data = DepartmentCreate(
            title="Test Department",
            created_by_id=1,  # Assuming a user with ID 1 exists
            process_ids=[1],  # Assuming a process with ID 1 exists
        )

        # Call the create_department method
        created_department = await self.service.create_department(department_data)

        # Assertions
        assert created_department is not None
        assert created_department.title == department_data.title
        assert created_department.created_by_id == department_data.created_by_id
        assert len(created_department.processes) == 1
        assert created_department.processes[0].id == department_data.process_ids[0]
        assert created_department.id is not None

    async def test_create_department_failure(self):
        """Test failure case for 'create_department' with invalid data"""
        # Simulating an invalid created_by_id (non-existing user)
        invalid_department_data = DepartmentCreate(
            title="Invalid Department",
            created_by_id=99999,  # Assuming this user does not exist
            process_ids=[1],
        )

        # Check if it raises an HTTPException with appropriate status code
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_department(invalid_department_data)

        assert excinfo.value.status_code == 500
        # Foreign key violation should be in the error message
        assert (
            "ForeignKeyViolationError" in str(excinfo.value.detail)
            or "foreign key" in str(excinfo.value.detail).lower()
        )

    async def test_get_departments(self):
        """Test retrieving a list of departments with pagination"""
        # Create a department to ensure we have at least one in the database
        department_data = DepartmentCreate(
            title="Department for List Test", created_by_id=1, process_ids=[]
        )
        await self.service.create_department(department_data)

        # Test the get_departments method with default pagination
        departments = await self.service.get_departments()

        # Assertions
        assert isinstance(departments, list)
        assert len(departments) > 0

        # Test pagination with limit
        limited_departments = await self.service.get_departments(limit=1)
        assert len(limited_departments) <= 1

        # Test pagination with offset
        offset_departments = await self.service.get_departments(offset=1, limit=10)
        if len(departments) > 1:
            # If we have more than one department, the first department with offset should differ
            assert offset_departments[0].id != departments[0].id

    async def test_get_department_by_id(self):
        """Test retrieving a single department by ID"""
        # Create a department to get a valid ID
        department_data = DepartmentCreate(
            title="Department for Get Test", created_by_id=1, process_ids=[1]
        )
        created_department = await self.service.create_department(department_data)
        department_id = created_department.id

        # Test getting the department by ID
        retrieved_department = await self.service.get_department_by_id(department_id)

        # Assertions
        assert retrieved_department is not None
        assert retrieved_department.id == department_id
        assert retrieved_department.title == department_data.title
        assert retrieved_department.created_by_id == department_data.created_by_id
        assert len(retrieved_department.processes) == 1

    async def test_get_department_by_id_not_found(self):
        """Test 404 error when department ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_department_by_id(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_department(self):
        """Test updating an existing department"""
        # Create a department to update
        department_data = DepartmentCreate(
            title="Original Department Title", created_by_id=1, process_ids=[]
        )
        created_department = await self.service.create_department(department_data)
        department_id = created_department.id

        # Update data
        update_data = DepartmentUpdate(
            title="Updated Department Title",
            process_ids=[1],  # Assuming process with ID 1 exists
        )

        # Update the department
        updated_department = await self.service.update_department(department_id, update_data)

        # Assertions
        assert updated_department.id == department_id
        assert updated_department.title == update_data.title
        assert len(updated_department.processes) == 1
        assert updated_department.processes[0].id == update_data.process_ids[0]

        # Original data should be preserved if not included in update
        assert updated_department.created_by_id == department_data.created_by_id

    async def test_update_department_not_found(self):
        """Test update with non-existent department ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        update_data = DepartmentUpdate(title="Updated Title")

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_department(non_existent_id, update_data)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_department_invalid_relationships(self):
        """Test update with invalid relationship IDs"""
        # Create a department to update
        department_data = DepartmentCreate(
            title="Department for Invalid Update", created_by_id=1, process_ids=[]
        )
        created_department = await self.service.create_department(department_data)
        department_id = created_department.id

        # Update with invalid process ID
        invalid_update = DepartmentUpdate(
            title="Updated with Invalid Process",
            process_ids=[99999],  # Assuming this process ID doesn't exist
        )

        # Check if it raises an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_department(department_id, invalid_update)

        assert excinfo.value.status_code == 500

    async def test_delete_department(self):
        """Test deleting a department"""
        # Create a department to delete
        department_data = DepartmentCreate(
            title="Department to Delete", created_by_id=1, process_ids=[]
        )
        created_department = await self.service.create_department(department_data)
        department_id = created_department.id

        # Delete the department
        await self.service.delete_department(department_id)

        # Verify it's deleted by trying to get it
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_department_by_id(department_id)

        assert excinfo.value.status_code == 404

    async def test_delete_department_not_found(self):
        """Test delete with non-existent department ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.delete_department(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_delete_department_exception(self):
        """Test that exceptions during department deletion are handled correctly"""
        # Create a department to get a valid ID
        department_data = DepartmentCreate(
            title="Department for Exception Test", created_by_id=1, process_ids=[]
        )
        created_department = await self.service.create_department(department_data)
        department_id = created_department.id

        # Mock the session's delete method to raise an exception
        original_delete = self.service.session.delete

        async def mock_delete_with_exception(*args, **kwargs):
            raise Exception("Database error during delete")

        # Replace the delete method with our mocked version
        self.service.session.delete = mock_delete_with_exception

        try:
            # The delete operation should now raise an HTTPException
            with pytest.raises(HTTPException) as excinfo:
                await self.service.delete_department(department_id)

            # Verify the exception details
            assert excinfo.value.status_code == 500
            assert "Database error during delete" in str(excinfo.value.detail)
        finally:
            # Restore the original delete method
            self.service.session.delete = original_delete
