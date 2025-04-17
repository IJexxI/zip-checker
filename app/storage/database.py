from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Text, DateTime, LargeBinary
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from uuid import uuid4
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://keycloak:password@postgres:5432/zipchecker"
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Upload(Base):
    __tablename__ = "Uploads"  # Сохраняем регистр
    id = Column(String, primary_key=True)
    filename = Column(String)
    file_content = Column(LargeBinary, nullable=True)  # Позволяем NULL
    status = Column(String)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")

async def save_file(file_bytes: bytes, filename: str) -> str:
    task_id = str(uuid4())
    logger.info(f"Attempting to save file with task_id: {task_id}, filename: {filename}")
    try:
        async with async_session() as session:
            async with session.begin():
                upload = Upload(
                    id=task_id,
                    filename=filename,
                    file_content=file_bytes,
                    status="pending"
                )
                session.add(upload)
                logger.info(f"Added upload to session: {task_id}")
                await session.commit()
                logger.info(f"Committed transaction for task_id: {task_id}")
        return task_id
    except Exception as e:
        logger.error(f"Failed to save file for task_id {task_id}: {str(e)}", exc_info=True)
        raise

async def get_result(task_id: str):
    logger.info(f"Fetching result for task_id: {task_id}")
    try:
        async with async_session() as session:
            result = await session.execute(
                text('SELECT status, result FROM "Uploads" WHERE id = :id'),
                {"id": task_id}
            )
            row = result.fetchone()
            if row and row[0] == "completed" and row[1]:
                return row[1]
            logger.warning(f"No completed result for task_id: {task_id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching result for task_id {task_id}: {str(e)}", exc_info=True)
        raise

async def set_result(task_id: str, result: dict):
    logger.info(f"Setting result for task_id: {task_id}")
    try:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    text('UPDATE "Uploads" SET result = :result, status = :status WHERE id = :id'),
                    {"id": task_id, "result": str(result), "status": "completed"}
                )
                await session.commit()
                logger.info(f"Result set for task_id: {task_id}")
    except Exception as e:
        logger.error(f"Error setting result for task_id {task_id}: {str(e)}", exc_info=True)
        raise

async def cleanup_old_files():
    threshold = datetime.utcnow() - timedelta(hours=1)
    logger.info(f"Running cleanup for files older than {threshold}")
    try:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    text('DELETE FROM "Uploads" WHERE created_at < :threshold'),
                    {"threshold": threshold}
                )
                await session.commit()
                logger.info("Cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
        raise

def start_cleanup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_old_files, "interval", hours=1)
    scheduler.start()
    logger.info("Cleanup scheduler started")