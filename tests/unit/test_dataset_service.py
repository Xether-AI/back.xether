"""Unit tests for Dataset Service with mocking."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services import dataset as dataset_service
from app.models.base import Dataset, DatasetVersion
from app.schemas.dataset import DatasetCreate, DatasetVersionCreate

@pytest.mark.asyncio
async def test_create_dataset_unit():
    """Test registering a new dataset."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    dataset_in = DatasetCreate(name="D1", project_id=1, storage_path="/path")
    
    with patch("app.services.dataset.events.publish", new_callable=AsyncMock) as mock_publish:
        dataset = await dataset_service.create_dataset(mock_db, dataset_in)
        
        assert dataset.name == "D1"
        assert mock_db.add.called
        assert mock_publish.called

@pytest.mark.asyncio
async def test_create_dataset_version_unit():
    """Test creating a dataset version."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    version_in = DatasetVersionCreate(version="v1", storage_path="/v1")
    
    with patch("app.services.dataset.events.publish", new_callable=AsyncMock):
        version = await dataset_service.create_dataset_version(mock_db, dataset_id=1, version_in=version_in)
        
        assert version.version == "v1"
        assert mock_db.add.called
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_list_project_datasets_unit():
    """Test listing project datasets."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [Dataset(id=1, name="D1")]
    mock_db.execute.return_value = mock_result
    
    datasets = await dataset_service.list_project_datasets(mock_db, project_id=1)
    
    assert len(datasets) == 1
    assert datasets[0].name == "D1"
