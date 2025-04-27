import pytest
from app.domains.role.role_schemas import RoleCreate, RoleUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domains.role.role_dependencies import get_role_service
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
@pytest.mark.integration
class TestRoleService:
    @pytest.fixture(autouse=True)
    async def setup(self, db_session: AsyncSession):
        """Fixture to set up any common state before each test."""
        self.service = get_role_service(db_session)

    async def test_create_role_integration(self):
        """Test the 'create_role' method"""
        # Prepare test data
        role_data = RoleCreate(
            title="Test Role",
            created_by_id=1,  # Assuming a user with ID 1 exists
            process_ids=[1]   # Assuming a process with ID 1 exists
        )
        
        # Call the create_role method
        created_role = await self.service.create_role(role_data)

        # Assertions
        assert created_role is not None
        assert created_role.title == role_data.title
        assert created_role.created_by_id == role_data.created_by_id
        assert len(created_role.processes) == 1
        assert created_role.processes[0].id == role_data.process_ids[0]
        assert created_role.id is not None

    async def test_create_role_failure(self):
        """Test failure case for 'create_role' with invalid data"""
        # Simulating an invalid created_by_id (non-existing user)
        invalid_role_data = RoleCreate(
            title="Invalid Role",
            created_by_id=99999,  # Assuming this user does not exist
            process_ids=[1]
        )

        # Check if it raises an HTTPException with appropriate status code
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_role(invalid_role_data)
        
        assert excinfo.value.status_code == 500
        # Foreign key violation should be in the error message
        assert "ForeignKeyViolationError" in str(excinfo.value.detail) or "foreign key" in str(excinfo.value.detail).lower()

    async def test_get_roles(self):
        """Test retrieving a list of roles with pagination"""
        # Create a role to ensure we have at least one in the database
        role_data = RoleCreate(
            title="Role for List Test",
            created_by_id=1,
            process_ids=[]
        )
        await self.service.create_role(role_data)
        
        # Test the get_roles method with default pagination
        roles = await self.service.get_roles()
        
        # Assertions
        assert isinstance(roles, list)
        assert len(roles) > 0
        
        # Test pagination with limit
        limited_roles = await self.service.get_roles(limit=1)
        assert len(limited_roles) <= 1
        
        # Test pagination with offset
        offset_roles = await self.service.get_roles(offset=1, limit=10)
        if len(roles) > 1:
            # If we have more than one role, the first role with offset should differ
            assert offset_roles[0].id != roles[0].id

    async def test_get_role_by_id(self):
        """Test retrieving a single role by ID"""
        # Create a role to get a valid ID
        role_data = RoleCreate(
            title="Role for Get Test",
            created_by_id=1,
            process_ids=[1]
        )
        created_role = await self.service.create_role(role_data)
        role_id = created_role.id
        
        # Test getting the role by ID
        retrieved_role = await self.service.get_role_by_id(role_id)
        
        # Assertions
        assert retrieved_role is not None
        assert retrieved_role.id == role_id
        assert retrieved_role.title == role_data.title
        assert retrieved_role.created_by_id == role_data.created_by_id
        assert len(retrieved_role.processes) == 1

    async def test_get_role_by_id_not_found(self):
        """Test 404 error when role ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        
        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_role_by_id(non_existent_id)
        
        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_role(self):
        """Test updating an existing role"""
        # Create a role to update
        role_data = RoleCreate(
            title="Original Role Title",
            created_by_id=1,
            process_ids=[]
        )
        created_role = await self.service.create_role(role_data)
        role_id = created_role.id
        
        # Update data
        update_data = RoleUpdate(
            title="Updated Role Title",
            process_ids=[1]  # Assuming process with ID 1 exists
        )
        
        # Update the role
        updated_role = await self.service.update_role(role_id, update_data)
        
        # Assertions
        assert updated_role.id == role_id
        assert updated_role.title == update_data.title
        assert len(updated_role.processes) == 1
        assert updated_role.processes[0].id == update_data.process_ids[0]
        
        # Original data should be preserved if not included in update
        assert updated_role.created_by_id == role_data.created_by_id

    async def test_update_role_not_found(self):
        """Test update with non-existent role ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        update_data = RoleUpdate(title="Updated Title")
        
        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_role(non_existent_id, update_data)
        
        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_role_invalid_relationships(self):
        """Test update with invalid relationship IDs"""
        # Create a role to update
        role_data = RoleCreate(
            title="Role for Invalid Update",
            created_by_id=1,
            process_ids=[]
        )
        created_role = await self.service.create_role(role_data)
        role_id = created_role.id
        
        # Update with invalid process ID
        invalid_update = RoleUpdate(
            title="Updated with Invalid Process",
            process_ids=[99999]  # Assuming this process ID doesn't exist
        )
        
        # Check if it raises an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_role(role_id, invalid_update)
        
        assert excinfo.value.status_code == 500

    async def test_delete_role(self):
        """Test deleting a role"""
        # Create a role to delete
        role_data = RoleCreate(
            title="Role to Delete",
            created_by_id=1,
            process_ids=[]
        )
        created_role = await self.service.create_role(role_data)
        role_id = created_role.id
        
        # Delete the role
        await self.service.delete_role(role_id)
        
        # Verify it's deleted by trying to get it
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_role_by_id(role_id)
        
        assert excinfo.value.status_code == 404

    async def test_delete_role_not_found(self):
        """Test delete with non-existent role ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        
        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.delete_role(non_existent_id)
        
        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_delete_role_exception(self):
        """Test that exceptions during role deletion are handled correctly"""
        # Create a role to get a valid ID
        role_data = RoleCreate(
            title="Role for Exception Test",
            created_by_id=1,
            process_ids=[]
        )
        created_role = await self.service.create_role(role_data)
        role_id = created_role.id
        
        # Mock the session's delete method to raise an exception
        original_delete = self.service.session.delete
        
        async def mock_delete_with_exception(*args, **kwargs):
            raise Exception("Database error during delete")
        
        # Replace the delete method with our mocked version
        self.service.session.delete = mock_delete_with_exception
        
        try:
            # The delete operation should now raise an HTTPException
            with pytest.raises(HTTPException) as excinfo:
                await self.service.delete_role(role_id)
            
            # Verify the exception details
            assert excinfo.value.status_code == 500
            assert "Database error during delete" in str(excinfo.value.detail)
        finally:
            # Restore the original delete method
            self.service.session.delete = original_delete 