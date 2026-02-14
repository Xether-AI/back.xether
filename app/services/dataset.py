"""Dataset service logic."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Dataset, DatasetVersion
from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetVersionCreate
from app.services.events import events


async def create_dataset(db: AsyncSession, dataset_in: DatasetCreate) -> Dataset:
    """Register a new dataset."""
    db_dataset = Dataset(
        name=dataset_in.name,
        description=dataset_in.description,
        project_id=dataset_in.project_id,
        storage_path=dataset_in.storage_path,
        meta_data=dataset_in.meta_data,
    )
    db.add(db_dataset)
    await db.commit()
    await db.refresh(db_dataset)
    
    await events.publish("dataset.created", {"dataset_id": db_dataset.id, "project_id": dataset_in.project_id}, resource_id=db_dataset.id)
    
    return db_dataset



async def get_dataset(db: AsyncSession, dataset_id: int) -> Optional[Dataset]:
    """Get a dataset by ID."""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    return result.scalars().first()


async def list_project_datasets(db: AsyncSession, project_id: int) -> List[Dataset]:
    """List all datasets in a project."""
    result = await db.execute(select(Dataset).where(Dataset.project_id == project_id))
    return list(result.scalars().all())


async def update_dataset(db: AsyncSession, db_dataset: Dataset, dataset_in: DatasetUpdate) -> Dataset:
    """Update dataset details."""
    update_data = dataset_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dataset, field, value)
    db.add(db_dataset)
    await db.commit()
    await db.refresh(db_dataset)
    
    await events.publish("dataset.updated", {"dataset_id": db_dataset.id}, resource_id=db_dataset.id)
    
    return db_dataset


async def delete_dataset(db: AsyncSession, dataset_id: int) -> bool:
    """Delete a dataset."""
    db_dataset = await get_dataset(db, dataset_id)
    if db_dataset:
        await db.delete(db_dataset)
        await db.commit()
        return True
    return False


async def create_dataset_version(
    db: AsyncSession, dataset_id: int, version_in: DatasetVersionCreate
) -> DatasetVersion:
    """Create a new dataset version."""
    db_version = DatasetVersion(
        dataset_id=dataset_id,
        version=version_in.version,
        meta_data=version_in.meta_data,
        storage_path=version_in.storage_path,
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    
    await events.publish("dataset.version_created", {"dataset_id": dataset_id, "version_id": db_version.id}, resource_id=dataset_id)
    
    return db_version


async def list_dataset_versions(db: AsyncSession, dataset_id: int) -> List[DatasetVersion]:
    """List all versions of a dataset."""
    result = await db.execute(select(DatasetVersion).where(DatasetVersion.dataset_id == dataset_id))
    return list(result.scalars().all())


async def get_dataset_version(db: AsyncSession, version_id: int) -> Optional[DatasetVersion]:
    """Get a dataset version by ID."""
    result = await db.execute(select(DatasetVersion).where(DatasetVersion.id == version_id))
    return result.scalars().first()
