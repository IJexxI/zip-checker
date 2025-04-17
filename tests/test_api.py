import pytest
from fastapi.testclient import TestClient
from app.main import app
import zipfile
import io
import os

client = TestClient(app)

@pytest.fixture
def test_zip_file():
    """Создаёт тестовый ZIP-файл."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("test.txt", "This is a test file.")
    zip_buffer.seek(0)
    return zip_buffer

def test_upload_zip(test_zip_file):
    """Тест загрузки ZIP-файла."""
    response = client.post(
        "/upload",
        files={"file": ("test.zip", test_zip_file, "application/zip")},
        headers={"Authorization": "Bearer test_token"}  # Заглушка для теста
    )
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_report_not_found():
    """Тест для несуществующего task_id."""
    response = client.get(
        "/report/12345",
        headers={"Authorization": "Bearer test_token"}  # Заглушка для теста
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_upload_invalid_file():
    """Тест загрузки не-ZIP файла."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", io.BytesIO(b"Not a ZIP"), "text/plain")},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 422
    assert "Invalid file format" in response.json()["detail"]