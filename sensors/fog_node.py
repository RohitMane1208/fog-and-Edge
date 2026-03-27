import sys
import os
import json
import time
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder

# Add fog_layer to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fog_layer.fog_processor import process_data

# Config
ENDPOINT = "a3s1uiaet0y05r-ats.iot.us-east-1.amazonaws.com"

CERT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-certificate.pem.crt"
KEY = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-private.pem.key"
ROOT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/AmazonRootCA1 (2).pem"

CLOUD_TOPIC = "solar/telemetry"
local_storage = {}

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global local_storage
    data = json.loads(payload)
    local_storage.update(data) # Merge new raw data into storage
    
    # Once we have enough data, process and push to cloud
    if "voltage" in local_storage and "temperature" in local_storage and "light_intensity" in local_storage:
        processed = process_data(local_storage)
        mqtt_connection.publish(topic=CLOUD_TOPIC, payload=json.dumps(processed), qos=QoS.AT_LEAST_ONCE)
        print("--- Fog Aggregation Sent to Cloud ---")

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT, cert_filepath=CERT, pri_key_filepath=KEY, ca_filepath=ROOT, client_id="fog_gateway_node"
)

mqtt_connection.connect().result()
# Subscribe to ALL raw topics
mqtt_connection.subscribe(topic="solar/raw/+", qos=QoS.AT_LEAST_ONCE, callback=on_message_received)

print("Fog Gateway Listening for Raw Sensors...")
while True:
    time.sleep(1)