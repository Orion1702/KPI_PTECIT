from paho.mqtt import client as mqtt_client
import time
from schema.aggregated_data_schema import AggregatedDataSchema
from schema.parking_schema import ParkingSchema
from file_datasource import FileDatasource
import config
import requests

def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print(f"Failed to connect {broker}:{port}, return code {rc}\n")
            exit(rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client

def publish(client, topic, parking_topic, datasource, delay):
    datasource.startReading()
    while True:
        time.sleep(delay)
        data = datasource.read()
        
        # 1. Робота з MQTT (Етап 1) [cite: 9]
        msg = AggregatedDataSchema().dumps(data)
        parking_msg = ParkingSchema().dumps(data.parking)
        for payload_mqtt, t in ((msg, topic), (parking_msg, parking_topic)):
            result = client.publish(t, payload_mqtt)
            if result[0] != 0:
                print(f"Failed to send message to topic {t}")

        # 2. Робота з Store API (Етап 2) [cite: 232-240]
        # Підготовка даних згідно зі схемою ProcessedAgentData
        payload_store = [{
            "road_state": "normal", 
            "agent_data": {
                "user_id": data.user_id,
                "accelerometer": {
                    "x": data.accelerometer.x,
                    "y": data.accelerometer.y,
                    "z": data.accelerometer.z
                },
                "gps": {
                    "latitude": data.gps.latitude,
                    "longitude": data.gps.longitude
                },
                "timestamp": data.timestamp.isoformat()
            }
        }]

        try:
            # Використовуємо URL з нашого config.py [cite: 64, 432]
            response = requests.post(
                f"{config.STORE_API_BASE_URL}/processed_agent_data/", 
                json=payload_store
            )
            if response.status_code == 200:
                print("Data sent to Store successfully")
            else:
                print(f"Store returned error: {response.status_code}")
        except Exception as e:
            print(f"Error sending data to Store: {e}")

def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    # Prepare datasource
    # datasource = FileDatasource(
    #     "data/data.csv",
    #     "data/gps_data.csv",
    #     "data/parking.csv",
    # )
    datasource = FileDatasource(
        "agent/src/data/data.csv",
        "agent/src/data/gps_data.csv",
        "agent/src/data/parking.csv",
    )
    # Infinity publish data
    publish(
        client,
        config.MQTT_TOPIC,
        config.MQTT_PARKING_TOPIC,
        datasource,
        config.DELAY,
    )

if __name__ == "__main__":
    run()