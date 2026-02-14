"""Unit tests for Project Service with mocking."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services import project as project_service
from app.models.base import Project
from app.schemas.project import ProjectCreate

@pytest.mark.asyncio
async def test_create_project_unit():
    """Test creating a new project."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    project_in = ProjectCreate(name="New Proj", description="Desc", team_id=1)
    
    project = await project_service.create_project(mock_db, project_in)
    
    assert project.name == "New Proj"
    assert project.team_id == 1
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_project_unit():
    """Test getting a project by ID."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_project = Project(id=1, name="P1")
    mock_result.scalars.return_value.first.return_value = mock_project
    mock_db.execute.return_value = mock_result
    
    project = await project_service.get_project(mock_db, 1)
    
    assert project is not None
    assert project.name == "P1"
    assert mock_db.execute.called

@pytest.mark.asyncio
async def test_list_team_projects_unit():
    """Test listing team projects."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_project = Project(id=1, name="P1", team_id=1)
    mock_result.scalars.return_value.all.return_value = [mock_project]
    mock_db.execute.return_value = mock_result
    
    projects = await project_service.list_team_projects(mock_db, team_id=1)
    
    assert len(projects) == 1
    assert projects[0].name == "P1"

@pytest.mark.asyncio
async def test_delete_project_unit():
    """Test deleting a project."""
    mock_db = AsyncMock()
    mock_project = Project(id=1, name="P1")
    
    with patch("app.services.project.get_project", return_value=mock_project):
        result = await project_service.delete_project(mock_db, 1)
        
        assert result is True
        assert mock_db.delete.called
        assert mock_db.commit.called
