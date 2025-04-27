# app/domains/role/role_service.py
# This file contains the service layer for the role domain

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.role.role_schemas import RoleCreate, RoleUpdate
from app.domains.role.role_model import Role
from app.domains.process.process_model import Process

class RoleService:
    """Service class for handling role-related operations"""
    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role"""
        role = Role(
            name=role_data.name,
            description=role_data.description,
            created_by_id=role_data.created_by_id
        )
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        
        # Handle processes if provided
        if role_data.process_ids is not None:
            await self._update_process_relationships(role, role_data.process_ids)
            
        return role

    async def get_roles(self, offset: int = 0, limit: int = 100) -> List[Role]:
        """Get a list of roles with pagination"""
        query = select(Role).options(
            selectinload(Role.processes),
            selectinload(Role.created_by)
        ).offset(offset).limit(limit)
        result = await self.session.execute(query)
        roles = result.scalars().all()
        return roles

    async def get_role_by_id(self, role_id: int) -> Role:
        """Get a role by its ID"""
        query = select(Role).options(
            selectinload(Role.processes),
            selectinload(Role.created_by)
        ).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalars().first()
        
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        
        return role

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """Update an existing role"""
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalars().first()
        
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        
        # Update fields if provided
        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        
        # Handle processes if provided
        if role_data.process_ids is not None:
            await self._update_process_relationships(role, role_data.process_ids)
        
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def delete_role(self, role_id: int) -> None:
        """Delete a role by its ID and clear all of its relationships"""
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalars().first()
        
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        
        # Clear all relationships first to ensure link table entries are removed
        role.processes = []
        await self.session.commit()
        
        # Now delete the role
        await self.session.delete(role)
        await self.session.commit()
        
    async def _update_process_relationships(self, role: Role, process_ids: List[int]) -> None:
        """Update the processes associated with a role
        
        This replaces all existing associations with the new ones provided.
        
        Args:
            role: The role to update
            process_ids: List of process IDs to associate with the role
        """
        # Clear existing relationships
        role.processes = []
        
        if process_ids:
            # Get all processes by their IDs
            result = await self.session.execute(
                select(Process).where(Process.id.in_(process_ids))
            )
            processes = result.scalars().all()
            
            # Check if any process IDs were not found
            found_ids = {process.id for process in processes}
            missing_ids = set(process_ids) - found_ids
            
            if missing_ids:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Some Process IDs not found: {missing_ids}"
                )
            
            # Update the relationships
            role.processes = processes
            
        await self.session.commit()
        await self.session.refresh(role)
