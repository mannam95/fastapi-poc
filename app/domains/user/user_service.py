# app/domains/user/user_service.py
# This file contains the business logic for the user domain

from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_database import AsyncDatabaseSessionManager
from app.core.exceptions import NotFoundException
from app.core.logging_service import BaseLoggingService
from app.domains.shared.base_service import BaseService
from app.domains.user.user_model import User
from app.domains.user.user_schemas import UserCreate, UserUpdate


class UserService(BaseService):
    """Service for user-related operations"""

    def __init__(
        self,
        session: AsyncSession,
        async_db_session_manager: AsyncDatabaseSessionManager,
        logging_service: BaseLoggingService,
    ):
        """Initialize the service with a database session and logging service

        Args:
            session: SQLAlchemy async session for database operations
            logging_service: Service for logging operations
        """
        super().__init__(session, async_db_session_manager, logging_service)

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

        # Log the creation
        await self.logging_service.log_business_event(
            "user_created",
            {
                "user_id": db_user.id,
                "title": db_user.title,
                "created_at": db_user.created_at.isoformat(),
            },
        )

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

        # Log the retrieval
        await self.logging_service.log_business_event(
            "users_retrieved",
            {
                "count": len(users),
                "offset": offset,
                "limit": limit,
            },
        )

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

        # Log the retrieval
        await self.logging_service.log_business_event(
            "user_retrieved",
            {
                "user_id": user_id,
                "title": user.title,
            },
        )

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

        # Store old values for logging
        old_title = user.title

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

        # Log the update
        await self.logging_service.log_business_event(
            "user_updated",
            {
                "user_id": user_id,
                "old_title": old_title,
                "new_title": user.title,
            },
        )

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

        # Store values for logging
        title = user.title

        # Delete the user
        await self.session.delete(user)

        # Commit all
        await self.session.commit()

        # Log the deletion
        await self.logging_service.log_business_event(
            "user_deleted",
            {
                "user_id": user_id,
                "title": title,
            },
        )
