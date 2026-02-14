"""Project management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.base import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services import project as project_service
from app.services import team as team_service

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a new project."""
    # Check if user has access to the team and permissions to create projects
    role = await team_service.get_user_role_in_team(db, team_id=project_in.team_id, user_id=current_user.id)
    if role not in ["admin", "manager"] and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions in the team to create projects",
        )
    
    return await project_service.create_project(db, project_in=project_in)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    team_id: int | None = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List projects user has access to, optionally filtered by team."""
    if team_id:
        role = await team_service.get_user_role_in_team(db, team_id=team_id, user_id=current_user.id)
        if not role and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await project_service.list_team_projects(db, team_id=team_id)
    
    return await project_service.list_user_projects(db, user_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get project details."""
    project = await project_service.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check if user has access to the team
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update project details."""
    project = await project_service.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check permissions (manager or admin in the team)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role not in ["admin", "manager"] and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await project_service.update_project(db, db_project=project, project_in=project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a project."""
    project = await project_service.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Check permissions (admin in the team or team owner)
    role = await team_service.get_user_role_in_team(db, team_id=project.team_id, user_id=current_user.id)
    if role != "admin" and not current_user.is_superuser:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only team admins can delete projects")
    
    await project_service.delete_project(db, project_id=project_id)
