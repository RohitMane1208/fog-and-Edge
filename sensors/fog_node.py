import sys
import os
import json
import time
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder

# Path setup to import fog_processor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fog_layer.fog_processor import process_data

# AWS IoT Core Configuration
ENDPOINT = "a3s1uiaet0y05r-ats.iot.us-east-1.amazonaws.com"
CERT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-certificate.pem.crt"
KEY = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-private.pem.key"
ROOT = "/mnt/c/Users/Rohit/Desktop/fog-and-Edge/certs/AmazonRootCA1 (2).pem"

CLOUD_TOPIC = "solar/telemetry"

# Global buffer to store the latest raw sensor readings
local_storage = {
    "voltage": None,
    "current": None,
    "temperature": None,
    "light_intensity": None,
    "humidity": None
}

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    """
    Function functionality preserved: Merges new raw data into storage.
    Now acts strictly as a data collector (buffer).
    """
    global local_storage
    try:
        data = json.loads(payload)
        local_storage.update(data)
    except Exception as e:
        print(f"Error buffering sensor data: {e}")

# Build mTLS Connection
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT, 
    cert_filepath=CERT, 
    pri_key_filepath=KEY, 
    ca_filepath=ROOT, 
    client_id="fog_gateway_node"
)

# Connect
mqtt_connection.connect().result()
print("Connected to AWS IoT Core!")

# Subscribe to ALL raw topics from edge sensors
mqtt_connection.subscribe(
    topic="solar/raw/+", 
    qos=QoS.AT_LEAST_ONCE, 
    callback=on_message_received
)

print("Fog Gateway Listening and Synchronizing to 5s Heartbeat...")

try:
    while True:
        # Wait for the synchronization interval
        time.sleep(5)

        # Function functionality preserved: Check if required data exists
        if (local_storage.get("voltage") is not None and 
            local_storage.get("temperature") is not None and 
            local_storage.get("light_intensity") is not None):
            
            # Process data (calculates power and local_alert)
            # Using .copy() ensures the buffer isn't modified while processing
            processed = process_data(local_storage.copy())
            
            # Publish aggregated packet to the cloud topic
            mqtt_connection.publish(
                topic=CLOUD_TOPIC, 
                payload=json.dumps(processed), 
                qos=QoS.AT_LEAST_ONCE
            )
            
            print(f"--- Fog Aggregation Sent to Cloud (Alert: {processed.get('local_alert')}) ---")
        else:
            print("--- Waiting for all sensors to report at least once... ---")

except KeyboardInterrupt:
    print("Shutting down Fog Node...")
    mqtt_connection.disconnect().result()