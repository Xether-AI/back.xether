"""Project service logic."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
    """Create a new project."""
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
        team_id=project_in.team_id,
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    """Get a project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalars().first()


async def list_team_projects(db: AsyncSession, team_id: int) -> List[Project]:
    """List all projects in a team."""
    result = await db.execute(select(Project).where(Project.team_id == team_id))
    return list(result.scalars().all())


async def list_user_projects(db: AsyncSession, user_id: int) -> List[Project]:
    """List all projects for teams where the user is a member."""
    from app.models.base import TeamMember
    result = await db.execute(
        select(Project)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_project(db: AsyncSession, db_project: Project, project_in: ProjectUpdate) -> Project:
    """Update project details."""
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    """Delete a project."""
    db_project = await get_project(db, project_id)
    if db_project:
        await db.delete(db_project)
        await db.commit()
        return True
    return False
