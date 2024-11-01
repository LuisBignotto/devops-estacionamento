from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
import io
import detector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector_instance = detector.ParkingDetector()

@app.get("/")
async def get():
    return FileResponse("index.html")

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite("uploaded_image.jpg", image)
    return {"message": "Imagem recebida com sucesso."}

@app.post("/update_coordinates")
async def update_coordinates(request: Request):
    data = await request.json()
    detector_instance.update_coordinates(data["coordinates"])
    return {"status": "success"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    detector_instance.start_detection()
    try:
        while True:
            try:
                # Recebe e processa a imagem
                message = await websocket.receive()
                if message.get("type") == "websocket.disconnect":
                    print("Cliente desconectado")
                    break
                elif "bytes" in message:
                    frame_bytes = message["bytes"]
                    nparr = np.frombuffer(frame_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    processed_frame = detector_instance.detect_motion(frame)
                    _, buffer = cv2.imencode('.jpg', processed_frame)

                    await websocket.send_bytes(buffer.tobytes())
                else:
                    print("Mensagem não reconhecida:", message)
            except WebSocketDisconnect:
                print("Desconexão detectada no WebSocket")
                break
    finally:
        detector_instance.stop_detection()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
