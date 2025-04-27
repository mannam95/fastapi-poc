# app/domains/role/role_service.py
# This file contains the service layer for the role domain

from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.role.role_schemas import RoleCreate, RoleUpdate
from app.domains.role.role_model import Role
from app.domains.process.process_model import Process
from app.domains.shared.base_service import BaseService

class RoleService(BaseService):
    """Service class for handling role-related operations"""
    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        super().__init__(session)

    async def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role"""
        try:
            # Create a new role
            role = Role(
                title=role_data.title,
                created_by_id=role_data.created_by_id
            )

            # Add the role to the database to get an ID
            self.session.add(role)
        
            # Handle processes if provided
            await self._update_relationships(role, role_data.process_ids)

            # Finally commit all
            await self.session.commit()

            # refresh the role to get the latest data
            await self.session.refresh(role)
            
            # return the role
            return role
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_roles(self, offset: int = 0, limit: int = 100) -> List[Role]:
        """Get a list of roles with pagination and associated data"""
        # Get the roles with associated data
        query = select(Role).options(
            selectinload(Role.processes),
            selectinload(Role.created_by)
        ).offset(offset).limit(limit)
        result = await self.session.execute(query)

        # Convert the result to a list of roles
        roles = result.scalars().all()

        # return the roles
        return roles

    async def get_role_by_id(self, role_id: int) -> Role:
        """Get a role by its ID with associated data"""
        # Get the role by ID with associated data
        query = select(Role).options(
            selectinload(Role.processes),
            selectinload(Role.created_by)
        ).where(Role.id == role_id)
        result = await self.session.execute(query)

        # Convert the result to a single role
        role = result.scalars().first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")

        # return the role
        return role

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """Update an existing role"""
        # Get the role by ID
        role = await self.session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        
        try:
            # Update the role fields
            update_data = role_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:
                    setattr(role, key, value)
            
            # Handle relationships
            await self._update_relationships(role, role_data.process_ids)   
            
            # Finally commit all
            await self.session.commit()

            # refresh the role to get the latest data
            await self.session.refresh(role)

            # return the role
            return role
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_role(self, role_id: int) -> None:
        """Delete a role by its ID and clear all of its relationships"""
        # Get the role by ID
        role = await self.session.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        
        try:
            # Clear all relationships
            role.processes = []
            
            # Now delete the role
            await self.session.delete(role)
            
            # Finally commit all
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def _update_relationships(
        self, 
        role: Role, 
        process_ids: List[int]
    ) -> None:
        """Update the many-to-many relationships of a role
        
        This method handles adding and removing related entities based on the provided IDs.
        
        Args:
            role: The role to update
            process_ids: List of process IDs to associate with the role
        """
        if process_ids is not None:
            await self.update_many_to_many_relationship(
                role.processes, 
                Process, 
                process_ids
            )

        await self.session.commit()
        await self.session.refresh(role)
