from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
import asyncio

from .mqtt_client import start_mqtt_client
from .websocket_manager import manager
from .influx import get_historical_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mqtt_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_client
    loop = asyncio.get_event_loop() 
    mqtt_client = start_mqtt_client(loop)
    logger.info("Application startup complete")
    yield
    mqtt_client.loop_stop()
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan, title="Smart Grid Sensor Backend")

# Allow frontend from any origin (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Smart Grid Backend Running - MQTT → InfluxDB → WebSocket"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception:
        manager.disconnect(websocket)

@app.get("/analytics")
async def analytics(
    interval: str = Query("daily", pattern="^(daily|weekly|monthly|yearly)$"),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get aggregated historical data for charts
    """
    data = get_historical_data(interval=interval)
    return {"interval": interval, "data": data}
