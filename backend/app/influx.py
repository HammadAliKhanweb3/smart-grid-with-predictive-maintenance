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
        point = Point("sensor_readings") \
            .tag("device", device_id) \
            .field("input_voltage", float(data["input_voltage"])) \
            .field("out_current1", float(data["out_current1"])) \
            .field("out_voltage1", float(data["out_voltage1"])) \
            .field("out_current2", float(data["out_current2"])) \
            .field("out_voltage2", float(data["out_voltage2"])) \
            .field("out_current3", float(data["out_current3"])) \
            .field("out_voltage3", float(data["out_voltage3"]))

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        logger.info(f"Stored data for device: {device_id}")
    except Exception as e:
        logger.error(f"InfluxDB write error: {e}")

def get_historical_data(interval: str = "daily", days: int = 30):
    """
    Returns aggregated data for charts
    interval: daily, weekly, monthly, yearly
    """
    window_map = {
        "daily": "1d",
        "weekly": "7d",
        "monthly": "30d",
        "yearly": "365d"
    }
    window = window_map.get(interval, "1d")
    range_start = f"-{days}d" if interval == "daily" else f"-365d"

    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: {range_start})
      |> filter(fn: (r) => r._measurement == "sensor_readings")
      |> aggregateWindow(every: {window}, fn: mean, createEmpty: false)
      |> yield(name: "mean")
    '''
    try:
        tables = query_api.query(query)
        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time().isoformat(),
                    "device": record.values.get("device"),
                    "input_voltage": record.get_value(),
                    "field": record.get_field()
                })
        return results
    except Exception as e:
        logger.error(f"Query error: {e}")
        return []