from typing import List
from fastapi import APIRouter, status

from app.domains.department.department_schemas import (
    DepartmentCreate, 
    DepartmentRead, 
    DepartmentUpdate
)
from app.domains.department.department_dependencies import DepartmentServiceDep

router = APIRouter()

# CRUD operations

@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(
    service: DepartmentServiceDep,
    department_in: DepartmentCreate
):
    """Create a new department"""
    return await service.create_department(department_in)


@router.get("/", response_model=List[DepartmentRead])
async def read_departments(
    service: DepartmentServiceDep,
    offset: int = 0, 
    limit: int = 100,
):
    """Get list of departments"""
    return await service.get_departments(offset, limit)


@router.get("/{department_id}", response_model=DepartmentRead)
async def read_department(
    department_id: int,
    service: DepartmentServiceDep,
):
    """Get a single department by ID with all relationships loaded"""
    return await service.get_department_by_id(department_id)


@router.put("/{department_id}", response_model=DepartmentRead)
async def update_department(
    department_id: int,
    department_in: DepartmentUpdate,
    service: DepartmentServiceDep,
):
    """Update an existing department"""
    return await service.update_department(department_id, department_in)


@router.delete("/{department_id}", status_code=status.HTTP_200_OK)
async def delete_department(
    department_id: int,
    service: DepartmentServiceDep,
):
    """Delete a department"""
    await service.delete_department(department_id)
    return {"message": "Department deleted successfully"}
