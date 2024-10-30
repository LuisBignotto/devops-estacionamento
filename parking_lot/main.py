from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from detector import ParkingDetector
import uvicorn
import cv2

app = FastAPI()
detector = ParkingDetector()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="./", html=True), name="html")

@app.get("/camera_image")
async def camera_image():
    frame = detector.get_current_frame()
    if frame is None:
        return JSONResponse(content={"error": "Não foi possível capturar a imagem da câmera."}, status_code=500)
    _, img_encoded = cv2.imencode('.jpg', frame)
    return Response(content=img_encoded.tobytes(), media_type="image/jpeg")

@app.post("/update_coordinates")
async def update_coordinates(request: Request):
    data = await request.json()
    detector.update_coordinates(data)
    return {"status": "success"}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(detector.video_generator(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/status")
async def get_status():
    status = detector.get_status()
    return JSONResponse(content=status)

@app.on_event("startup")
async def startup_event():
    detector.start_detection()

@app.on_event("shutdown")
def shutdown_event():
    detector.stop_detection()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    
