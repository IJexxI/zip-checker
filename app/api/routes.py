from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.auth import verify_token
from app.storage.database import save_file, get_result
from app.services.zip_checker import dummy_check_zip
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/ping")
async def ping():
    logger.info("Ping requested")
    return {"message": "pong"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), payload=Depends(verify_token)):
    if not file.filename.endswith(".zip"):
        logger.warning(f"Invalid file format: {file.filename}")
        raise HTTPException(status_code=422, detail="Invalid file format. Only ZIP files are allowed")
    content = await file.read()
    task_id = await save_file(content, file.filename)
    logger.info(f"File uploaded successfully, task_id: {task_id}")
    asyncio.create_task(dummy_check_zip(task_id))
    return {"task_id": task_id}

@router.get("/report/{task_id}")
async def get_report(task_id: str, payload=Depends(verify_token)):
    result = await get_result(task_id)
    if result is None:
        logger.warning(f"Result not found for task_id: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "SUCCESS", "results": result}