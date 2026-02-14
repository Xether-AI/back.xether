"""Team management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.base import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamMember, TeamMemberAdd
from app.services import team as team_service

router = APIRouter()


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_new_team(
    *,
    db: AsyncSession = Depends(deps.get_db),
    team_in: TeamCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a new team."""
    return await team_service.create_team(db, team_in=team_in, owner_id=current_user.id)


@router.get("/", response_model=List[TeamResponse])
async def list_user_teams(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all teams the current user is a member of."""
    return await team_service.list_user_teams(db, user_id=current_user.id)


@router.get("/{team_id}", response_model=TeamResponse)
async def read_team(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get team details."""
    team = await team_service.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    # Check if user is a member
    role = await team_service.get_user_role_in_team(db, team_id=team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a team member")
    
    return team


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    team_in: TeamUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update team details (Admin or Owner only)."""
    team = await team_service.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    # Check permissions
    role = await team_service.get_user_role_in_team(db, team_id=team_id, user_id=current_user.id)
    if role != "admin" and team.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await team_service.update_team(db, db_team=team, team_in=team_in)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a team (Owner only)."""
    team = await team_service.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    if team.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can delete teams")
    
    await team_service.delete_team(db, team_id=team_id)


@router.post("/{team_id}/members", response_model=TeamMember)
async def add_member(
    team_id: int,
    member_in: TeamMemberAdd,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Add a member to the team (Admin or Owner only)."""
    team = await team_service.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    role = await team_service.get_user_role_in_team(db, team_id=team_id, user_id=current_user.id)
    if role != "admin" and team.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    return await team_service.add_team_member(db, team_id=team_id, member_in=member_in)


@router.get("/{team_id}/members", response_model=List[TeamMember])
async def list_members(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all team members."""
    # Check if user is a member
    role = await team_service.get_user_role_in_team(db, team_id=team_id, user_id=current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a team member")
    
    return await team_service.get_team_members(db, team_id=team_id)


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    team_id: int,
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Remove a member from the team (Admin or Owner only)."""
    team = await team_service.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    role = await team_service.get_user_role_in_team(db, team_id=team_id, user_id=current_user.id)
    if role != "admin" and team.owner_id != current_user.id and not current_user.is_superuser:
        # Users might be able to remove themselves?
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    # Cannot remove the owner
    if user_id == team.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the team owner")
        
    await team_service.remove_team_member(db, team_id=team_id, user_id=user_id)
