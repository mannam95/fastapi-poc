from typing import List

from fastapi import APIRouter, status

from app.domains.department.department_dependencies import DepartmentServiceDep
from app.domains.department.department_schemas import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
)

router = APIRouter()

# CRUD operations


@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(service: DepartmentServiceDep, department_in: DepartmentCreate):
    """
    Create a new department.

    Creates a department with specified attributes and optional
    associations to processes.

    Returns the newly created department with all details.
    """
    return await service.create_department(department_in)


@router.get("/", response_model=List[DepartmentRead])
async def read_departments(
    service: DepartmentServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get a list of departments with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns a list of departments with their details and process relationships.
    """
    return await service.get_departments(skip, limit)


@router.get("/{department_id}", response_model=DepartmentRead)
async def read_department(
    department_id: int,
    service: DepartmentServiceDep,
):
    """
    Get a single department by ID.

    Retrieves detailed information about a specific department,
    including its creator and associated processes.

    Raises 404 if department not found.
    """
    return await service.get_department_by_id(department_id)


@router.put("/{department_id}", response_model=DepartmentRead)
async def update_department(
    department_id: int,
    department_in: DepartmentUpdate,
    service: DepartmentServiceDep,
):
    """
    Update an existing department.

    Updates department attributes and/or process relationships.
    Supports partial updates (only specified fields will be updated).

    Returns the updated department with all details.
    Raises 404 if department not found.
    """
    return await service.update_department(department_id, department_in)


@router.delete("/{department_id}", status_code=status.HTTP_200_OK)
async def delete_department(
    department_id: int,
    service: DepartmentServiceDep,
):
    """
    Delete a department.

    Completely removes a department and its relationships.
    This operation cannot be undone.

    Returns a success message.
    Raises 404 if department not found.
    """
    await service.delete_department(department_id)
    return {"message": "Department deleted successfully"}
