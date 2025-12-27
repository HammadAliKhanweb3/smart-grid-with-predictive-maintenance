from dotenv import load_dotenv
import os

load_dotenv()

# InfluxDB Config
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")  
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# EMQX Cloud MQTT Config - CHANGE THESE TO YOUR EMQX CLOUD VALUES!
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensors/#")  # Subscribe to all sensor topics