import paho.mqtt.client as mqtt
import json
import logging
from .influx import write_point
from .websocket_manager import manager
from .config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_TOPIC
import asyncio
import uuid 

main_loop = None

logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connected to EMQX Cloud MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        logger.error(f"MQTT Connection failed with code {rc}")



def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic
        device_id = topic.split("/")[-1]  # e.g., sensors/smart-grid-unit-01 → smart-grid-unit-01

        logger.info(f"Received from {device_id}: {payload}")

        # Store in InfluxDB
        write_point(device_id, payload)

        # Broadcast to all WebSocket clients
        broadcast_data = {
            "device": device_id,
            "timestamp": payload.get("timestamp", None),
            "data": payload
        }

        if main_loop:
           main_loop.call_soon_threadsafe(
              lambda: asyncio.create_task(manager.broadcast(broadcast_data))
           )

    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

def start_mqtt_client(loop):
    global main_loop
    main_loop = loop
    unique_id = f"smart_grid_backend_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=unique_id,protocol=mqtt.MQTTv5)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()  # EMQX Cloud requires TLS
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"Connecting to EMQX Cloud: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    client.loop_start()  # Run in background thread
    return client