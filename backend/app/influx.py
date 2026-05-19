from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi
from .config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
import logging

logger = logging.getLogger(__name__)

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api: QueryApi = client.query_api()

def write_point(device_id: str, data: dict):
    try:
        # Ensure all fields are present to avoid pivot issues later
        point = Point("sensor_readings") \
            .tag("device", device_id) \
            .field("voltage_1", float(data.get("voltage_1", 0))) \
            .field("current_1", float(data.get("current_1", 0))) \
            .field("power_1", float(data.get("power_1", 0))) \
            .field("energy_1", float(data.get("energy_1", 0))) \
            .field("frequency_1", float(data.get("frequency_1", 0))) \
            .field("voltage_2", float(data.get("voltage_2", 0))) \
            .field("current_2", float(data.get("current_2", 0))) \
            .field("power_2", float(data.get("power_2", 0))) \
            .field("energy_2", float(data.get("energy_2", 0))) \
            .field("frequency_2", float(data.get("frequency_2", 0))) \
            .field("voltage_3", float(data.get("voltage_3", 0))) \
            .field("current_3", float(data.get("current_3", 0))) \
            .field("power_3", float(data.get("power_3", 0))) \
            .field("energy_3", float(data.get("energy_3", 0))) \
            .field("frequency_3", float(data.get("frequency_3", 0))) \
            .field("voltage_4", float(data.get("voltage_4", 0))) \
            .field("current_4", float(data.get("current_4", 0))) \
            .field("power_4", float(data.get("power_4", 0))) \
            .field("energy_4", float(data.get("energy_4", 0))) \
            .field("frequency_4", float(data.get("frequency_4", 0)))

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        logger.info(f"Stored data for device: {device_id}")
    except Exception as e:
        logger.error(f"InfluxDB write error: {e}")

def get_historical_data(interval: str = "daily"):
    config = {
        "daily":   {"range": "-24h", "window": "5m"},
        "weekly":  {"range": "-7d",  "window": "30m"},
        "monthly": {"range": "-30d", "window": "2h"},
        "yearly":  {"range": "-365d","window": "1d"},
    }
    
    settings = config.get(interval, config["daily"])

    # Updated Query with all 20 fields
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: {settings["range"]})
      |> filter(fn: (r) => r._measurement == "sensor_readings")
      |> aggregateWindow(every: {settings["window"]}, fn: mean, createEmpty: false)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''

    try:
        tables = query_api.query(query)
        results = []
        
        for table in tables:
            for record in table.records:
                # Return all 20 fields
                results.append({
                    "time": record.get_time().isoformat(),
                    "device": record.values.get("device"),
                    # Sensor 1 (Input)
                    "voltage_1": record.values.get("voltage_1"),
                    "current_1": record.values.get("current_1"),
                    "power_1": record.values.get("power_1"),
                    "energy_1": record.values.get("energy_1"),
                    "frequency_1": record.values.get("frequency_1"),
                    # Sensor 2 (Load 1)
                    "voltage_2": record.values.get("voltage_2"),
                    "current_2": record.values.get("current_2"),
                    "power_2": record.values.get("power_2"),
                    "energy_2": record.values.get("energy_2"),
                    "frequency_2": record.values.get("frequency_2"),
                    # Sensor 3 (Load 2)
                    "voltage_3": record.values.get("voltage_3"),
                    "current_3": record.values.get("current_3"),
                    "power_3": record.values.get("power_3"),
                    "energy_3": record.values.get("energy_3"),
                    "frequency_3": record.values.get("frequency_3"),
                    # Sensor 4 (Load 3)
                    "voltage_4": record.values.get("voltage_4"),
                    "current_4": record.values.get("current_4"),
                    "power_4": record.values.get("power_4"),
                    "energy_4": record.values.get("energy_4"),
                    "frequency_4": record.values.get("frequency_4"),
                })
        
        if not results:
            logger.warning(f"No data found for range {settings['range']} with window {settings['window']}")
            
        return results
    except Exception as e:
        logger.error(f"Query error: {e}")
        return []