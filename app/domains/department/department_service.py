# app/domains/department/department_service.py
# This file contains the business logic for the department domain

from typing import List, Optional
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
            
            # Handle processes if provided
            if department_data.process_ids is not None:
                await self._update_process_relationships(db_department, department_data.process_ids)
                
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
            # Update department fields
            update_data = department_data.model_dump(exclude={"process_ids"}, exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:  # Only update if the value is not None
                    setattr(department, key, value)
            
            # Handle processes if provided
            if department_data.process_ids is not None:
                await self._update_process_relationships(department, department_data.process_ids)
                
            await self.session.commit()
            await self.session.refresh(department)
            return department
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_department(self, department_id: int) -> None:
        """Delete a department and clear all of its relationships"""
        department = await self.session.get(Department, department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        try:
            # Clear all relationships first to ensure link table entries are removed
            department.processes = []
            await self.session.commit()
            
            # Now delete the department
            await self.session.delete(department)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    async def _update_process_relationships(self, department: Department, process_ids: List[int]) -> None:
        """Update the processes associated with a department
        
        This replaces all existing associations with the new ones provided.
        
        Args:
            department: The department to update
            process_ids: List of process IDs to associate with the department
        """
        # Clear existing relationships
        department.processes = []
        
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
            department.processes = processes
            
        await self.session.commit()
        await self.session.refresh(department) 