import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from main import app, detector_instance
import numpy as np
from fastapi.testclient import TestClient
from io import BytesIO
import cv2

client = TestClient(app)

@pytest.mark.asyncio
async def test_upload_image():
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    _, image_encoded = cv2.imencode('.jpg', image)
    image_bytes = BytesIO(image_encoded.tobytes())

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
        response = await client.post("/upload_image", files=files)
    
    assert response.status_code == 200
    assert response.json() == {"message": "Imagem recebida com sucesso."}

@pytest.mark.asyncio
async def test_update_coordinates():
    test_data = [{"coordinates": [{"x": 10, "y": 20}, {"x": 30, "y": 40}]}]
    detector_instance.update_coordinates = MagicMock()
    
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post("/update_coordinates", json={"coordinates": test_data})
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    detector_instance.update_coordinates.assert_called_once_with(test_data)

def test_websocket_endpoint():
    with client.websocket_connect("/ws") as websocket:
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        _, image_encoded = cv2.imencode('.jpg', image)
        websocket.send_bytes(image_encoded.tobytes())

        # Recebe a resposta
        data = websocket.receive_bytes()
        assert data is not None

def test_start_stop_detection():
    detector_instance.start_detection = MagicMock()
    detector_instance.stop_detection = MagicMock()
    
    detector_instance.start_detection()
    detector_instance.start_detection.assert_called_once()
    
    detector_instance.stop_detection()
    detector_instance.stop_detection.assert_called_once()
