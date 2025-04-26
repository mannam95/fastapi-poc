# app/domains/role/role_service.py
# This file contains the service layer for the role domain

from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domains.role.role_schemas import RoleCreate, RoleUpdate, RoleProcessAssociation
from app.domains.role.role_model import Role
from app.domains.process.process_model import Process
from app.domains.role.role_model import RoleProcess


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
            description=role_data.description
        )
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def get_roles(self, offset: int = 0, limit: int = 100) -> List[Role]:
        """Get a list of roles with pagination"""
        query = select(Role).options(
            joinedload(Role.processes)
        ).offset(offset).limit(limit)
        result = await self.session.execute(query)
        roles = result.scalars().all()
        return roles

    async def get_role_by_id(self, role_id: int) -> Role:
        """Get a role by its ID"""
        query = select(Role).options(
            joinedload(Role.processes)
        ).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalars().first()
        return role

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """Update an existing role"""
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalars().first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        await self.session.commit()
        await self.session.refresh(role)
        return role 

    async def delete_role(self, role_id: int) -> None:
        """Delete a role by its ID"""
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalars().first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        await self.session.delete(role)
        await self.session.commit()

    async def add_process_to_role(self, association: RoleProcessAssociation) -> RoleProcess:
        """Add a process to a role"""
        role = await self.session.get(Role, association.role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {association.role_id} not found")
        process = await self.session.get(Process, association.process_id)
        if not process:
            raise HTTPException(status_code=404, detail=f"Process with ID {association.process_id} not found")
        role.processes.append(process)
        await self.session.commit()
        await self.session.refresh(role, ['processes'])
        return role

    async def remove_process_from_role(self, role_id: int, process_id: int) -> None:
        """Remove a process from a role"""
        query = select(RoleProcess).where(
            RoleProcess.role_id == role_id,
            RoleProcess.process_id == process_id
        )
        result = await self.session.execute(query)
        association = result.scalars().first()
        if not association:
            raise HTTPException(status_code=404, detail=f"Process {process_id} is not associated with role {role_id}")
        await self.session.delete(association)
        await self.session.commit()