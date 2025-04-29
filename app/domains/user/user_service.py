# app/domains/user/user_service.py
# This file contains the business logic for the user domain

from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.domains.shared.base_service import BaseService
from app.domains.user.user_model import User
from app.domains.user.user_schemas import UserCreate, UserUpdate


class UserService(BaseService):
    """Service for user-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session

        Args:
            session: SQLAlchemy async session for database operations
        """
        super().__init__(session)

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            user_data: User creation data containing title

        Returns:
            User: The newly created user with database ID

        Raises:
            DatabaseException: If there's a database error
        """
        # Create new User instance from input data
        db_user = User(title=user_data.title, created_at=datetime.now())

        # Add the user to the database to get an ID
        self.session.add(db_user)

        # Commit all
        await self.session.commit()

        # Refresh the user to get the latest data
        await self.session.refresh(db_user)

        # Return the user
        return db_user

    async def get_users(self, offset: int = 0, limit: int = 100) -> List[User]:
        """
        Get a list of users with pagination.

        Args:
            offset: Number of records to offset (for pagination)
            limit: Maximum number of records to return

        Returns:
            List[User]: List of user objects

        Raises:
            DatabaseException: If there's a database error
        """
        # Get the users with pagination
        result = await self.session.execute(select(User).offset(offset).limit(limit))

        # Convert the result to a list of users
        users = list(result.scalars().all())

        # Return the users
        return users

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Get a single user by ID.

        Args:
            user_id: Database ID of the user to retrieve

        Returns:
            User: The requested user

        Raises:
            NotFoundException: If user not found
            DatabaseException: If there's a database error
        """
        # Get the user by ID
        user = await self.session.get(User, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        # Return the user
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Update an existing user's data.

        Args:
            user_id: Database ID of the user to update
            user_data: User update data containing fields to update

        Returns:
            User: The updated user

        Raises:
            NotFoundException: If user not found
            DatabaseException: If there's a database error
        """
        # Get the user by ID
        user = await self.session.get(User, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        # Get the update data
        update_data = user_data.model_dump(exclude_unset=True)

        # Apply updates
        for key, value in update_data.items():
            if value is not None:  # Only update if the value is not None
                setattr(user, key, value)

        # Commit all
        await self.session.commit()

        # Refresh the user to get the latest data
        await self.session.refresh(user)

        # Return the user
        return user

    async def delete_user(self, user_id: int) -> None:
        """
        Delete a user from the database.

        Args:
            user_id: Database ID of the user to delete

        Raises:
            NotFoundException: If user not found
            DatabaseException: If there's a database error
        """
        # Get the user by ID
        user = await self.session.get(User, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        # Delete the user
        await self.session.delete(user)

        # Commit all
        await self.session.commit()
