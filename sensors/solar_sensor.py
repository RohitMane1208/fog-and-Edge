import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
import json
import random
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder
from fog_layer.fog_processor import process_data

ENDPOINT = "a3s1uiaet0y05r-ats.iot.us-east-1.amazonaws.com"
TOPIC = "solar/Data"

CERT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-certificate.pem.crt"
KEY = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-private.pem.key"
ROOT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/AmazonRootCA1 (2).pem"

INTERVAL = 5


def generate_sensor_data():

    voltage = round(random.uniform(15, 22), 2)
    current = round(random.uniform(2, 8), 2)

    return {
        "panel_id": "SOLAR-001",
        "voltage": voltage,
        "current": current,
        "temperature": round(random.uniform(20, 85), 1),
        "light_intensity": random.randint(200, 1000),
        "humidity": round(random.uniform(30, 60), 1)
    }


mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERT,
    pri_key_filepath=KEY,
    ca_filepath=ROOT,
    client_id="solar_sensor_node"
)

print("Connecting sensor...")
mqtt_connection.connect().result()

print("Sensor started")

while True:

    raw_data = generate_sensor_data()

    processed_data = process_data(raw_data)

    mqtt_connection.publish(
        topic=TOPIC,
        payload=json.dumps(processed_data),
        qos=QoS.AT_LEAST_ONCE
    )

    print("Published:", processed_data)

    time.sleep(INTERVAL)