"""Unit tests for Pipeline Service with mocking."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services import pipeline as pipeline_service
from app.models.base import Pipeline, PipelineExecution
from app.schemas.pipeline import PipelineCreate

@pytest.mark.asyncio
async def test_create_pipeline_unit():
    """Test creating a new pipeline."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    pipeline_in = PipelineCreate(name="P1", project_id=1, config={"steps": []})
    
    with patch("app.services.pipeline.events.publish", new_callable=AsyncMock) as mock_publish:
        pipeline = await pipeline_service.create_pipeline(mock_db, pipeline_in)
        
        assert pipeline.name == "P1"
        assert mock_db.add.called
        assert mock_publish.called

@pytest.mark.asyncio
async def test_trigger_pipeline_execution_unit():
    """Test triggering a pipeline execution."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    
    with patch("app.services.pipeline.events.publish", new_callable=AsyncMock):
        execution = await pipeline_service.trigger_pipeline_execution(mock_db, pipeline_id=1)
        
        assert execution.status == "pending"
        assert mock_db.add.called
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_list_project_pipelines_unit():
    """Test listing project pipelines."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [Pipeline(id=1, name="P1")]
    mock_db.execute.return_value = mock_result
    
    pipelines = await pipeline_service.list_project_pipelines(mock_db, project_id=1)
    
    assert len(pipelines) == 1
    assert pipelines[0].name == "P1"

@pytest.mark.asyncio
async def test_update_pipeline_unit():
    """Test updating pipeline details."""
    mock_db = AsyncMock()
    mock_pipeline = Pipeline(id=1, name="Old P")
    update_in = PipelineUpdate(name="New P")
    
    with patch("app.services.pipeline.events.publish", new_callable=AsyncMock):
        updated = await pipeline_service.update_pipeline(mock_db, mock_pipeline, update_in)
        assert updated.name == "New P"
        assert mock_db.add.called

@pytest.mark.asyncio
async def test_delete_pipeline_unit():
    """Test deleting a pipeline."""
    mock_db = AsyncMock()
    mock_pipeline = Pipeline(id=1, name="P1")
    
    with patch("app.services.pipeline.get_pipeline", return_value=mock_pipeline):
        result = await pipeline_service.delete_pipeline(mock_db, pipeline_id=1)
        assert result is True
        assert mock_db.delete.called

@pytest.mark.asyncio
async def test_list_pipeline_executions_unit():
    """Test listing pipeline executions."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [PipelineExecution(id=1, status="success")]
    mock_db.execute.return_value = mock_result
    
    executions = await pipeline_service.list_pipeline_executions(mock_db, pipeline_id=1)
    assert len(executions) == 1
    assert executions[0].status == "success"

