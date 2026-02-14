"""Pipeline service logic."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Pipeline, PipelineExecution
from app.schemas.pipeline import PipelineCreate, PipelineUpdate


async def create_pipeline(db: AsyncSession, pipeline_in: PipelineCreate) -> Pipeline:
    """Create a new pipeline."""
    db_pipeline = Pipeline(
        name=pipeline_in.name,
        description=pipeline_in.description,
        project_id=pipeline_in.project_id,
        config=pipeline_in.config,
        is_active=pipeline_in.is_active,
    )
    db.add(db_pipeline)
    await db.commit()
    await db.refresh(db_pipeline)
    return db_pipeline


async def get_pipeline(db: AsyncSession, pipeline_id: int) -> Optional[Pipeline]:
    """Get a pipeline by ID."""
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    return result.scalars().first()


async def list_project_pipelines(db: AsyncSession, project_id: int) -> List[Pipeline]:
    """List all pipelines in a project."""
    result = await db.execute(select(Pipeline).where(Pipeline.project_id == project_id))
    return list(result.scalars().all())


async def update_pipeline(db: AsyncSession, db_pipeline: Pipeline, pipeline_in: PipelineUpdate) -> Pipeline:
    """Update pipeline details."""
    update_data = pipeline_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pipeline, field, value)
    db.add(db_pipeline)
    await db.commit()
    await db.refresh(db_pipeline)
    return db_pipeline


async def delete_pipeline(db: AsyncSession, pipeline_id: int) -> bool:
    """Delete a pipeline."""
    db_pipeline = await get_pipeline(db, pipeline_id)
    if db_pipeline:
        await db.delete(db_pipeline)
        await db.commit()
        return True
    return False


async def trigger_pipeline_execution(db: AsyncSession, pipeline_id: int, meta_data: Optional[dict] = None) -> PipelineExecution:
    """Trigger a new pipeline execution."""
    db_execution = PipelineExecution(
        pipeline_id=pipeline_id,
        status="pending",
        meta_data=meta_data,
    )
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)
    return db_execution


async def list_pipeline_executions(db: AsyncSession, pipeline_id: int) -> List[PipelineExecution]:
    """List all executions of a pipeline."""
    result = await db.execute(
        select(PipelineExecution)
        .where(PipelineExecution.pipeline_id == pipeline_id)
        .order_by(PipelineExecution.started_at.desc())
    )
    return list(result.scalars().all())


async def get_pipeline_execution(db: AsyncSession, execution_id: int) -> Optional[PipelineExecution]:
    """Get a pipeline execution by ID."""
    result = await db.execute(select(PipelineExecution).where(PipelineExecution.id == execution_id))
    return result.scalars().first()
