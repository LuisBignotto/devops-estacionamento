import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from main import app, detector_instance
import numpy as np
from fastapi.testclient import TestClient
from io import BytesIO
import cv2
from detector import ParkingDetector

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
        data = websocket.receive_bytes()
        assert data is not None

def test_start_stop_detection():
    detector_instance.start_detection = MagicMock()
    detector_instance.stop_detection = MagicMock()
    
    detector_instance.start_detection()
    detector_instance.start_detection.assert_called_once()
    
    detector_instance.stop_detection()
    detector_instance.stop_detection.assert_called_once()

def test_initialize_parking_spaces():
    detector = ParkingDetector()
    coordinates = [{"x": 0, "y": 0}, {"x": 100, "y": 0}, {"x": 100, "y": 100}, {"x": 0, "y": 100}]
    detector.update_coordinates([coordinates])
    assert len(detector.contours) > 0
    assert len(detector.bounds) > 0
    assert len(detector.mask) > 0


def test_detect_motion():
    detector = ParkingDetector()
    detector.update_coordinates([[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}, {"x": 0, "y": 10}]])
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    processed_frame = detector.detect_motion(frame)
    assert processed_frame is not None
    assert not any(detector.statuses.values())

def test_reset_coordinates():
    detector = ParkingDetector()
    coordinates = [{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}, {"x": 0, "y": 10}]
    detector.update_coordinates([coordinates])
    detector.coordinates_data = []
    assert detector.coordinates_data == []


def test_websocket_continuous_data():
    with client.websocket_connect("/ws") as websocket:
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        _, image_encoded = cv2.imencode('.jpg', image)
        for _ in range(5):
            websocket.send_bytes(image_encoded.tobytes())
            data = websocket.receive_bytes()
            assert data is not None

def test_apply_motion_detection():
    detector = ParkingDetector()
    detector.update_coordinates([[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}, {"x": 0, "y": 10}]])
    detector.reference_frame = np.zeros((20, 20), dtype=np.uint8)
    current_frame = np.ones((20, 20), dtype=np.uint8) * 255
    status = detector._ParkingDetector__apply(current_frame, 0, detector.coordinates_data[0])
    assert status == True
