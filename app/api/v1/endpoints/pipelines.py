"""Pipeline management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.base import User
from app.schemas.pipeline import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    PipelineExecutionResponse,
)
from app.services import pipeline as pipeline_service
from app.services import project as project_service
from app.services import team as team_service

router = APIRouter()


@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_new_pipeline(
    *,
    db: AsyncSession = Depends(deps.get_db),
    pipeline_in: PipelineCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a new pipeline."""
    project = await project_service.get_project(db, project_id=pipeline_in.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager", "developer"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await pipeline_service.create_pipeline(db, pipeline_in=pipeline_in)


@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List pipelines in a project."""
    project = await project_service.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return await pipeline_service.list_project_pipelines(db, project_id=project_id)


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def read_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get pipeline details."""
    pipeline = await pipeline_service.get_pipeline(db, pipeline_id=pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    
    project = await project_service.get_project(db, project_id=pipeline.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return pipeline


@router.patch("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    pipeline_in: PipelineUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update pipeline details."""
    pipeline = await pipeline_service.get_pipeline(db, pipeline_id=pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    
    project = await project_service.get_project(db, project_id=pipeline.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager", "developer"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await pipeline_service.update_pipeline(db, db_pipeline=pipeline, pipeline_in=pipeline_in)


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a pipeline."""
    pipeline = await pipeline_service.get_pipeline(db, pipeline_id=pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    
    project = await project_service.get_project(db, project_id=pipeline.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    await pipeline_service.delete_pipeline(db, pipeline_id=pipeline_id)


@router.post("/{pipeline_id}/execute", response_model=PipelineExecutionResponse, status_code=status.HTTP_201_CREATED)
async def execute_pipeline(
    pipeline_id: int,
    meta_data: dict | None = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Trigger a new pipeline execution."""
    pipeline = await pipeline_service.get_pipeline(db, pipeline_id=pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    
    project = await project_service.get_project(db, project_id=pipeline.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager", "developer"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await pipeline_service.trigger_pipeline_execution(db, pipeline_id=pipeline_id, meta_data=meta_data)


@router.get("/{pipeline_id}/executions", response_model=List[PipelineExecutionResponse])
async def list_executions(
    pipeline_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all executions of a pipeline."""
    pipeline = await pipeline_service.get_pipeline(db, pipeline_id=pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    
    project = await project_service.get_project(db, project_id=pipeline.project_id)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return await pipeline_service.list_pipeline_executions(db, pipeline_id=pipeline_id)
