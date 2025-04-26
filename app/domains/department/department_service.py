# app/domains/department/department_service.py
# This file contains the business logic for the department domain

from typing import List
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.department.department_model import Department
from app.domains.department.department_schemas import DepartmentCreate, DepartmentUpdate
from app.domains.process.process_model import Process


class DepartmentService:
    """Service for department-related operations"""

    def __init__(self, session: AsyncSession):
        """Initialize the service with a database session
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def create_department(self, department_data: DepartmentCreate) -> Department:
        """Create a new department"""
        try:
            # Create new Department instance from input data
            db_department = Department(
                title=department_data.title,
                created_by_id=department_data.created_by_id
            )
            
            # Add the department to the database to get an ID
            self.session.add(db_department)    
            await self.session.commit()
            await self.session.refresh(db_department)
            return db_department
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_departments(self, offset: int = 0, limit: int = 100) -> List[Department]:
        """Get a list of departments with pagination and associated data"""
        result = await self.session.execute(
            select(Department)
            .options(
                selectinload(Department.created_by),
                selectinload(Department.processes)
            )
            .offset(offset)
            .limit(limit)
        )
        departments = result.scalars().all()
        return departments

    async def get_department_by_id(self, department_id: int) -> Department:
        """Get a single department by ID with associated data"""
        result = await self.session.execute(
            select(Department)
            .options(
                selectinload(Department.created_by),
                selectinload(Department.processes)
            )
            .where(Department.id == department_id)
        )
        department = result.scalars().first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        return department

    async def update_department(self, department_id: int, department_data: DepartmentUpdate) -> Department:
        """Update an existing department"""
        department = await self.session.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        try:
            update_data = department_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(department, key, value)
            await self.session.commit()
            await self.session.refresh(department, ['created_by', 'processes'])
            return department
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_department(self, department_id: int) -> Department:
        """Delete a department"""
        department = await self.session.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        try:
            await self.session.delete(department)
            await self.session.commit()
            return department
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    # Methods for managing process associations
    
    async def add_process_to_department(self, department_id: int, process_id: int) -> Department:
        """Add a process to a department"""
        department = await self.session.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
            
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
            
        try:
            department.processes.append(process)
            await self.session.commit()
            await self.session.refresh(department, ['processes'])
            return department
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    async def remove_process_from_department(self, department_id: int, process_id: int) -> Department:
        """Remove a process from a department"""
        department = await self.session.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
            
        process = await self.session.get(Process, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
            
        try:
            if process in department.processes:
                department.processes.remove(process)
                await self.session.commit()
                await self.session.refresh(department, ['processes'])
            return department
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e)) 