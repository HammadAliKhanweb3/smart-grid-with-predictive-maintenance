# backend/test_publisher.py
import paho.mqtt.client as mqtt
import json
import time
import random
import uuid

# === YOUR CORRECT EMQX CLOUD SETTINGS ===
BROKER = "h84fb003.ala.asia-southeast1.emqxsl.com"
PORT = 8883
USERNAME = "Hammad"
PASSWORD = "Hammad@123"
TOPIC = "sensors/smart-grid-unit-01"

# Generate a unique client ID
CLIENT_ID = f"test_publisher_{uuid.uuid4().hex[:8]}"

# Use callback API version 2 to avoid deprecation warning
client = mqtt.Client(
    client_id=CLIENT_ID,
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Successfully connected to EMQX Cloud!")
    else:
        print(f"❌ Connection failed with code: {reason_code}")

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"✅ Published message ID: {mid}")

client.on_connect = on_connect
client.on_publish = on_publish

print(f"Connecting to {BROKER}:{PORT} with Client ID: {CLIENT_ID}...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

print("Publishing fake sensor data every 5 seconds... Press Ctrl+C to stop")

try:
    while True:
        data = {
            # Sensor 1 (Input)
            "voltage_1": round(random.uniform(220.0, 240.0), 3),
            "current_1": round(random.uniform(5.0, 32.0), 3),
            "power_1": round(random.uniform(1100.0, 7680.0), 3),
            "energy_1": round(random.uniform(0.0, 100.0), 3),
            "frequency_1": round(random.uniform(49.5, 50.5), 2),
            
            # Sensor 2 (Load 1)
            "voltage_2": round(random.uniform(47.0, 49.0), 3),
            "current_2": round(random.uniform(0.0, 15.0), 3),
            "power_2": round(random.uniform(0.0, 735.0), 3),
            "energy_2": round(random.uniform(0.0, 50.0), 3),
            "frequency_2": round(random.uniform(49.5, 50.5), 2),
            
            # Sensor 3 (Load 2)
            "voltage_3": round(random.uniform(47.0, 49.0), 3),
            "current_3": round(random.uniform(0.0, 10.0), 3),
            "power_3": round(random.uniform(0.0, 490.0), 3),
            "energy_3": round(random.uniform(0.0, 30.0), 3),
            "frequency_3": round(random.uniform(49.5, 50.5), 2),
            
            # Sensor 4 (Load 3)
            "voltage_4": round(random.uniform(0.0, 49.0), 3),
            "current_4": round(random.uniform(0.0, 8.0), 3),
            "power_4": round(random.uniform(0.0, 392.0), 3),
            "energy_4": round(random.uniform(0.0, 20.0), 3),
            "frequency_4": round(random.uniform(49.5, 50.5), 2),
        }
        
        payload = json.dumps(data)
        result = client.publish(TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nStopped publishing")
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from broker")