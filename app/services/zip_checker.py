import asyncio
import zipfile
import io
from sqlalchemy.sql import text
from app.storage.database import async_session, set_result
from app.services.characteristics import (
    check_antivirus,
    check_structure,
    check_archive_size
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_zip_integrity(file_bytes: bytes) -> dict:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            test_result = zf.testzip()
            return {"valid": test_result is None, "error": test_result}
    except zipfile.BadZipFile:
        return {"valid": False, "error": "Invalid ZIP file"}

async def dummy_check_zip(task_id: str):
    logger.info(f"Starting check for task_id: {task_id}")
    async with async_session() as session:
        result = await session.execute(
            text('SELECT filename, file_content FROM "Uploads" WHERE id = :id'),
            {"id": task_id}
        )
        row = result.fetchone()
    if not row:
        logger.error(f"Upload not found for task_id: {task_id}")
        return

    filename, file_bytes = row
    if file_bytes is None:
        logger.error(f"No file content for task_id: {task_id}")
        return

    logger.info(f"Processing file {filename} for task_id: {task_id}")

    integrity_task = check_zip_integrity(file_bytes)
    antivirus_task = check_antivirus(file_bytes)
    structure_task = check_structure(file_bytes)
    size_task = check_archive_size(file_bytes)

    integrity, antivirus, structure, size_result = await asyncio.gather(
        integrity_task, antivirus_task, structure_task, size_task
    )

    final_result = {
        "integrity": integrity,
        "antivirus": antivirus,
        "structure": structure,
        "size": size_result
    }

    await set_result(task_id, final_result)
    logger.info(f"Check completed for task_id: {task_id}")