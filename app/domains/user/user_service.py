# app/domains/user/user_service.py
# This file contains the business logic for the user domain

from typing import List
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.user_model import User
from app.domains.user.user_schemas import UserCreate, UserUpdate


class UserService:
    """Service for user-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Create new User instance from input data
            db_user = User(
                title=user_data.title,
                created_at=datetime.now()
            )
            
            # Add the user to the database to get an ID
            self.session.add(db_user)
    
            # Commit all
            await self.session.commit()
            
            # Refresh the user to get the latest data
            await self.session.refresh(db_user)
            
            # Return the user
            return db_user
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get a list of users with pagination"""
        # Get the users with pagination
        result = await self.session.execute(
            select(User)
            .offset(skip)
            .limit(limit)
        )

        # Convert the result to a list of users
        users = result.scalars().all()

        # Return the users
        return users

    async def get_user_by_id(self, user_id: int) -> User:
        """Get a single user by ID"""
        # Get the user by ID
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the user
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update an existing user"""
        # Get the user by ID
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        try:
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
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_user(self, user_id: int) -> None:
        """Delete a user"""
        # Get the user by ID
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            # Delete the user
            await self.session.delete(user)

            # Commit all
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e)) 