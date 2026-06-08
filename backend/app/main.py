# from fastapi import FastAPI, WebSocket, Query
# from fastapi.middleware.cors import CORSMiddleware
# import logging
# from contextlib import asynccontextmanager
# import asyncio

# from .mqtt_client import start_mqtt_client
# from .websocket_manager import manager
# from .influx import get_historical_data

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# mqtt_client = None

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global mqtt_client
#     loop = asyncio.get_event_loop() 
#     mqtt_client = start_mqtt_client(loop)
#     logger.info("Application startup complete")
#     yield
#     mqtt_client.loop_stop()
#     logger.info("Application shutdown")

# app = FastAPI(lifespan=lifespan, title="Smart Grid Sensor Backend")

# # Allow frontend from any origin (adjust in production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# async def root():
#     return {"message": "Smart Grid Backend Running - MQTT → InfluxDB → WebSocket"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             await websocket.receive_text()  # Keep connection alive
#     except Exception:
#         manager.disconnect(websocket)

# @app.get("/analytics")
# async def analytics(
#     interval: str = Query("daily", pattern="^(daily|weekly|monthly|yearly)$"),
#     days: int = Query(30, ge=1, le=365)
# ):
#     """
#     Get aggregated historical data for charts
#     """
#     data = get_historical_data(interval=interval)
#     return {"interval": interval, "data": data}

from fastapi import FastAPI, WebSocket, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    logger.info("Application startup complete and MQTT client initialized")
    yield
    if mqtt_client:
        try:
            mqtt_client.loop_stop()
            logger.info("MQTT client loop stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping MQTT loop during shutdown: {e}")
    logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan, title="Smart Grid Sensor Backend")

# Allow frontend from any origin (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── RELAY CONTROL INTERFACE REQUIREMENT ──────────────────────────────────────

class RelayControlPayload(BaseModel):
    relay_id: str  # Will receive 'r1', 'r2', or 'r3' from the dashboard
    status: bool   # true for turning ON, false for turning OFF

# ─── HTTP ROUTE DEFINITIONS ───────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Smart Grid Backend Running - MQTT → InfluxDB → WebSocket"}


@app.post("/api/relay/toggle")
async def toggle_relay(payload: RelayControlPayload):
    """
    Endpoint called by Next.js to forward switch actions directly to the ESP32
    """
    global mqtt_client
    
    if not mqtt_client:
        logger.error("Relay switch command failed: MQTT client instance is missing")
        raise HTTPException(status_code=503, detail="MQTT interface driver is currently offline")
        
    # Translate the boolean status into the string instructions the ESP32 expects
    command_msg = "ON" if payload.status else "OFF"
    
    # Target topic matches the format your ESP32's wildcard wildcard pattern listens to
    target_topic = f"smartgrid/control/{payload.relay_id}"
    
    try:
        logger.info(f"Dispatching directive execution: {command_msg} -> Topic: {target_topic}")
        
        # Publish command with QoS 1 to guarantee delivery across the broker network
        mqtt_client.publish(target_topic, command_msg, qos=1)
        
        return {
            "success": True, 
            "message": f"Successfully published directive '{command_msg}' to node '{payload.relay_id}'"
        }
    except Exception as e:
        logger.error(f"Failed to submit hardware execution payload over broker: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Broker Error: Could not dispatch control packet")


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