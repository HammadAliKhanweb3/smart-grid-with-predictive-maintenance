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
            .field("input_current", float(data.get("input_current", 0))) \
            .field("input_voltage", float(data.get("input_voltage", 0))) \
            .field("out_current1", float(data.get("out_current1", 0))) \
            .field("out_voltage1", float(data.get("out_voltage1", 0))) \
            .field("out_current2", float(data.get("out_current2", 0))) \
            .field("out_voltage2", float(data.get("out_voltage2", 0))) \
            .field("out_current3", float(data.get("out_current3", 0))) \
            .field("out_voltage3", float(data.get("out_voltage3", 0)))

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

    # Updated Query: Includes group() to ensure all fields are processed together before pivot
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
                # We use .get() on record.values because pivot turns fields into dictionary keys
                results.append({
                    "time": record.get_time().isoformat(),
                    "device": record.values.get("device"),
                    "input_voltage": record.values.get("input_voltage"),
                    "input_current": record.values.get("input_current"),
                    "out_voltage1": record.values.get("out_voltage1"),
                    "out_current1": record.values.get("out_current1"),
                    "out_voltage2": record.values.get("out_voltage2"),
                    "out_current2": record.values.get("out_current2"),
                    "out_voltage3": record.values.get("out_voltage3"),
                    "out_current3": record.values.get("out_current3"),
                })
        
        # If results is still empty, it means the range/window didn't find data
        if not results:
            logger.warning(f"No data found for range {settings['range']} with window {settings['window']}")
            
        return results
    except Exception as e:
        logger.error(f"Query error: {e}")
        return []