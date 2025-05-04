import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.user_dependencies import get_user_service
from app.domains.user.user_schemas import UserCreate, UserUpdate
from app.utils.logging_service import get_logging_service


@pytest.mark.asyncio
@pytest.mark.integration
class TestUserService:
    @pytest.fixture(autouse=True)
    async def setup(self, db_session: AsyncSession):
        """Fixture to set up any common state before each test."""
        self.service = get_user_service(db_session, get_logging_service())

    async def test_create_user_integration(self):
        """Test the 'create_user' method"""
        # Prepare test data
        user_data = UserCreate(title="Test User")

        # Call the create_user method
        created_user = await self.service.create_user(user_data)

        # Assertions
        assert created_user is not None
        assert created_user.title == user_data.title
        assert created_user.id is not None
        assert created_user.created_at is not None

    async def test_get_users(self):
        """Test retrieving a list of users with pagination"""
        # Create a user to ensure we have at least one in the database
        user_data = UserCreate(title="User for List Test")
        await self.service.create_user(user_data)

        # Test the get_users method with default pagination
        users = await self.service.get_users()

        # Assertions
        assert isinstance(users, list)
        assert len(users) > 0

        # Test pagination with limit
        limited_users = await self.service.get_users(limit=1)
        assert len(limited_users) <= 1

        # Test pagination with skip
        skip_users = await self.service.get_users(offset=1, limit=10)
        if len(users) > 1:
            # If we have more than one user, the first user with skip should differ
            assert skip_users[0].id != users[0].id

    async def test_get_user_by_id(self):
        """Test retrieving a single user by ID"""
        # Create a user to get a valid ID
        user_data = UserCreate(title="User for Get Test")
        created_user = await self.service.create_user(user_data)
        user_id = created_user.id

        # Test getting the user by ID
        retrieved_user = await self.service.get_user_by_id(user_id)

        # Assertions
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.title == user_data.title
        assert retrieved_user.created_at is not None

    async def test_get_user_by_id_not_found(self):
        """Test 404 error when user ID doesn't exist"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_user_by_id(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_update_user(self):
        """Test updating an existing user"""
        # Create a user to update
        user_data = UserCreate(title="Original User Title")
        created_user = await self.service.create_user(user_data)
        user_id = created_user.id

        # Update data
        update_data = UserUpdate(title="Updated User Title")

        # Update the user
        updated_user = await self.service.update_user(user_id, update_data)

        # Assertions
        assert updated_user.id == user_id
        assert updated_user.title == update_data.title
        assert updated_user.created_at is not None

    async def test_update_user_not_found(self):
        """Test update with non-existent user ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999
        update_data = UserUpdate(title="Updated Title")

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.update_user(non_existent_id, update_data)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()

    async def test_delete_user(self):
        """Test deleting a user"""
        # Create a user to delete
        user_data = UserCreate(title="User to Delete")
        created_user = await self.service.create_user(user_data)
        user_id = created_user.id

        # Delete the user
        await self.service.delete_user(user_id)

        # Verify it's deleted by trying to get it
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_user_by_id(user_id)

        assert excinfo.value.status_code == 404

    async def test_delete_user_not_found(self):
        """Test delete with non-existent user ID"""
        # Use a very large ID that's unlikely to exist
        non_existent_id = 99999

        # Check if it raises an HTTPException with status code 404
        with pytest.raises(HTTPException) as excinfo:
            await self.service.delete_user(non_existent_id)

        assert excinfo.value.status_code == 404
        assert "not found" in str(excinfo.value.detail).lower()
