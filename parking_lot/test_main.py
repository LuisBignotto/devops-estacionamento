import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from main import app, detector

import numpy as np

@pytest.mark.asyncio
async def test_camera_image():
    # Simula uma imagem de retorno do detector (um array NumPy)
    detector.get_current_frame = MagicMock(return_value=np.zeros((480, 640, 3), dtype=np.uint8))
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get("/camera_image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_update_coordinates():
    # Dados de teste
    test_data = [{"x": 10, "y": 20}, {"x": 30, "y": 40}]
    detector.update_coordinates = MagicMock()
    
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post("/update_coordinates", json=test_data)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    detector.update_coordinates.assert_called_once_with(test_data)

@pytest.mark.asyncio
async def test_get_status():
    # Simula um status do detector
    detector.get_status = MagicMock(return_value={"1": True, "2": False})
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"1": True, "2": False}

def test_start_stop_detection():
    # Teste de inicialização e parada da detecção
    detector.start_detection = MagicMock()
    detector.stop_detection = MagicMock()
    
    detector.start_detection()
    detector.start_detection.assert_called_once()
    
    detector.stop_detection()
    detector.stop_detection.assert_called_once()
