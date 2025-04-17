import asyncio
import random

async def check_antivirus(file_bytes: bytes) -> dict:
    await asyncio.sleep(1)  # имитация задержки
    return {
        "malware_detected": False,
        "engine_version": "AV 1.2.3"
    }

async def check_structure(file_bytes: bytes) -> dict:
    await asyncio.sleep(1)
    return {
        "files_inside": random.randint(1, 10),
        "compressed_size_mb": round(len(file_bytes) / 1024 / 1024, 2)
    }

async def check_archive_size(file_bytes: bytes) -> dict:
    max_size_mb = 10
    size_mb = len(file_bytes) / 1024 / 1024

    return {
        "valid": size_mb <= max_size_mb,
        "size_mb": round(size_mb, 2),
        "limit_mb": max_size_mb
    }