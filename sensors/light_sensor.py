import time
import json
import random
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder

# Config (Same as your original)
ENDPOINT = "a3s1uiaet0y05r-ats.iot.us-east-1.amazonaws.com"

CERT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-certificate.pem.crt"
KEY = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-private.pem.key"
ROOT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/AmazonRootCA1 (2).pem"
TOPIC = "solar/raw/light"

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT, cert_filepath=CERT, pri_key_filepath=KEY, ca_filepath=ROOT, client_id="light_sensor_node"
)

mqtt_connection.connect().result()
print("Light Sensor Active...")

while True:
    data = {
        "panel_id": "SOLAR-001",
        "light_intensity": random.randint(200, 1000),
        "timestamp": int(time.time())
    }
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(data), qos=QoS.AT_LEAST_ONCE)
    print(f"Sent Light Intensity: {data}")
    time.sleep(5)