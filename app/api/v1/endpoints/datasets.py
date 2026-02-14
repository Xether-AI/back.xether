"""Dataset registry endpoints."""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.base import User
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    DatasetVersionCreate,
    DatasetVersionResponse,
)
from app.services import dataset as dataset_service
from app.services import project as project_service
from app.services import team as team_service

router = APIRouter()


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_new_dataset(
    *,
    db: AsyncSession = Depends(deps.get_db),
    dataset_in: DatasetCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Register a new dataset."""
    project = await project_service.get_project(db, project_id=dataset_in.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check permissions (Developer or above in the team)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager", "developer"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await dataset_service.create_dataset(db, dataset_in=dataset_in)


@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List datasets in a project."""
    project = await project_service.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return await dataset_service.list_project_datasets(db, project_id=project_id)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def read_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get dataset details."""
    dataset = await dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    project = await project_service.get_project(db, project_id=dataset.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return dataset


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    dataset_in: DatasetUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update dataset details."""
    dataset = await dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    project = await project_service.get_project(db, project_id=dataset.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager", "developer"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await dataset_service.update_dataset(db, db_dataset=dataset, dataset_in=dataset_in)


@router.delete("/{dataset_id}", status_code=status.HTTP_304_NOT_MODIFIED)
async def delete_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a dataset."""
    dataset = await dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    project = await project_service.get_project(db, project_id=dataset.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    await dataset_service.delete_dataset(db, dataset_id=dataset_id)


@router.post("/{dataset_id}/versions", response_model=DatasetVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    dataset_id: int,
    version_in: DatasetVersionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a new dataset version."""
    dataset = await dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    project = await project_service.get_project(db, project_id=dataset.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager", "developer"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await dataset_service.create_dataset_version(db, dataset_id=dataset_id, version_in=version_in)


@router.get("/{dataset_id}/versions", response_model=List[DatasetVersionResponse])
async def list_versions(
    dataset_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all versions of a dataset."""
    dataset = await dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    project = await project_service.get_project(db, project_id=dataset.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return await dataset_service.list_dataset_versions(db, dataset_id=dataset_id)
