"""Team service logic."""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Team, TeamMember, User
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberAdd
from app.db.redis import cache, invalidate_cache
from app.services.events import events


async def create_team(db: AsyncSession, team_in: TeamCreate, owner_id: int) -> Team:
    """Create a new team and add the owner as an admin member."""
    db_team = Team(
        name=team_in.name,
        description=team_in.description,
        owner_id=owner_id,
    )
    db.add(db_team)
    await db.flush()  # Get the team ID
    
    # Add owner as admin member
    member = TeamMember(
        team_id=db_team.id,
        user_id=owner_id,
        role="admin"
    )
    db.add(member)
    
    await db.commit()
    await db.refresh(db_team)
    
    await events.publish("team.created", {"team_id": db_team.id, "owner_id": owner_id}, resource_id=db_team.id)
    
    return db_team


async def get_team(db: AsyncSession, team_id: int) -> Optional[Team]:
    """Get a team by ID."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    return result.scalars().first()


async def list_user_teams(db: AsyncSession, user_id: int) -> List[Team]:
    """List teams where the user is a member or owner."""
    result = await db.execute(
        select(Team)
        .join(TeamMember)
        .where(TeamMember.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_team(db: AsyncSession, db_team: Team, team_in: TeamUpdate) -> Team:
    """Update team details."""
    update_data = team_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_team, field, value)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    
    await invalidate_cache("team", db_team.id)
    await events.publish("team.updated", {"team_id": db_team.id}, resource_id=db_team.id)
    
    return db_team


async def delete_team(db: AsyncSession, team_id: int) -> bool:
    """Delete a team."""
    db_team = await get_team(db, team_id)
    if db_team:
        await db.delete(db_team)
        await db.commit()
        return True
    return False


async def add_team_member(db: AsyncSession, team_id: int, member_in: TeamMemberAdd) -> TeamMember:
    """Add a member to a team."""
    member = TeamMember(
        team_id=team_id,
        user_id=member_in.user_id,
        role=member_in.role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def remove_team_member(db: AsyncSession, team_id: int, user_id: int) -> bool:
    """Remove a member from a team."""
    result = await db.execute(
        select(TeamMember).where(
            and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        )
    )
    member = result.scalars().first()
    if member:
        await db.delete(member)
        await db.commit()
        return True
    return False


async def get_team_members(db: AsyncSession, team_id: int) -> List[TeamMember]:
    """Get all members of a team."""
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    return list(result.scalars().all())


async def get_user_role_in_team(db: AsyncSession, team_id: int, user_id: int) -> Optional[str]:
    """Get the role of a user in a team."""
    result = await db.execute(
        select(TeamMember.role).where(
            and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()
