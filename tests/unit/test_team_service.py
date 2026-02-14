"""Unit tests for Team Service with mocking."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services import team as team_service
from app.models.base import Team, TeamMember
from app.schemas.team import TeamCreate, TeamMemberAdd

@pytest.mark.asyncio
async def test_create_team_unit():
    """Test creating a new team and owner membership."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    team_in = TeamCreate(name="New Team", description="Desc")
    
    with patch("app.services.team.events.publish", new_callable=AsyncMock) as mock_publish:
        team = await team_service.create_team(mock_db, team_in, owner_id=1)
        
        assert team.name == "New Team"
        assert team.owner_id == 1
        assert mock_db.add.call_count == 2 # Team and TeamMember
        assert mock_db.commit.called
        assert mock_publish.called

@pytest.mark.asyncio
async def test_add_team_member_unit():
    """Test adding a member to a team."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    member_in = TeamMemberAdd(user_id=2, role="developer")
    
    member = await team_service.add_team_member(mock_db, team_id=1, member_in=member_in)
    
    assert member.user_id == 2
    assert member.role == "developer"
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_user_role_in_team_unit():
    """Test getting user role in team."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = "admin"
    mock_db.execute.return_value = mock_result
    
    role = await team_service.get_user_role_in_team(mock_db, team_id=1, user_id=1)
    
    assert role == "admin"
    assert mock_db.execute.called

@pytest.mark.asyncio
async def test_list_user_teams_unit():
    """Test listing user teams."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_team = Team(id=1, name="T1")
    mock_result.scalars.return_value.all.return_value = [mock_team]
    mock_db.execute.return_value = mock_result
    
    teams = await team_service.list_user_teams(mock_db, user_id=1)
    
@pytest.mark.asyncio
async def test_remove_team_member_unit():
    """Test removing a member from a team."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_member = TeamMember(team_id=1, user_id=1)
    mock_result.scalars.return_value.first.return_value = mock_member
    mock_db.execute.return_value = mock_result
    
    success = await team_service.remove_team_member(mock_db, team_id=1, user_id=1)
    
    assert success is True
    assert mock_db.delete.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_team_members_unit():
    """Test getting all members of a team."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [TeamMember(team_id=1, user_id=1)]
    mock_db.execute.return_value = mock_result
    
    members = await team_service.get_team_members(mock_db, team_id=1)
    
    assert len(members) == 1
    assert mock_db.execute.called

@pytest.mark.asyncio
async def test_update_team_unit():
    """Test updating team details."""
    mock_db = AsyncMock()
    mock_team = Team(id=1, name="Old")
    from app.schemas.team import TeamUpdate
    update_in = TeamUpdate(name="New")
    
    with patch("app.services.team.invalidate_cache", new_callable=AsyncMock), \
         patch("app.services.team.events.publish", new_callable=AsyncMock):
        updated = await team_service.update_team(mock_db, mock_team, update_in)
        assert updated.name == "New"
        assert mock_db.add.called

@pytest.mark.asyncio
async def test_delete_team_unit():
    """Test deleting a team."""
    mock_db = AsyncMock()
    mock_team = Team(id=1, name="T1")
    with patch("app.services.team.get_team", return_value=mock_team):
        result = await team_service.delete_team(mock_db, team_id=1)
        assert result is True
        assert mock_db.delete.called

@pytest.mark.asyncio
async def test_remove_team_member_fail_unit():
    """Test removing non-existent team member."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result
    
    success = await team_service.remove_team_member(mock_db, team_id=1, user_id=99)
    assert success is False


