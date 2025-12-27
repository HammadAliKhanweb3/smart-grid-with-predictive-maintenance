# backend/test_publisher.py
import paho.mqtt.client as mqtt
import json
import time
import random

# === YOUR EMQX CLOUD SETTINGS ===
BROKER = "td182d6f.ala.asia-southeast1.emqxsl.com"
PORT = 8883                                          # TLS port
USERNAME = "Hammad"
PASSWORD = "Hammad@123"
TOPIC = "sensors/smart-grid-unit-01"

# Create client with modern API (removes deprecation warning)
client = mqtt.Client(protocol=mqtt.MQTTv5)

# Authentication
client.username_pw_set(USERNAME, PASSWORD)

# === CRITICAL: Enable TLS for EMQX Cloud ===
client.tls_set()  # This is REQUIRED on port 8883

# Optional: Better logging
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Successfully connected to EMQX Cloud!")
    else:
        print(f"❌ Connection failed with code: {rc}")

def on_publish(client, userdata, mid):
    print(f"✅ Published message ID: {mid}")

client.on_connect = on_connect
client.on_publish = on_publish

# Connect
print(f"Connecting to {BROKER}:{PORT} ...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

print("Publishing fake sensor data every 5 seconds... Press Ctrl+C to stop")

try:
    while True:
        data = {
            "input_voltage": round(random.uniform(220.0, 240.0), 3),
            "out_current1": round(random.uniform(0.0, 15.0), 3),
            "out_voltage1": round(random.uniform(47.0, 49.0), 3),
            "out_current2": round(random.uniform(0.0, 10.0), 3),
            "out_voltage2": round(random.uniform(47.0, 49.0), 3),
            "out_current3": round(random.uniform(0.0, 8.0), 3),
            "out_voltage3": round(random.uniform(0.0, 49.0), 3),
        }
        payload = json.dumps(data)
        result = client.publish(TOPIC, payload)
        
        # Print immediately (result may be async)
        print(f"Published to {TOPIC}: {data}")
        
        time.sleep(5)
except KeyboardInterrupt:
    print("\nStopped publishing")
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from broker")