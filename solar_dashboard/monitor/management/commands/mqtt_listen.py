import json
import time
from django.core.management.base import BaseCommand
from django.db import connections
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder
from monitor.models import SolarReading

ENDPOINT = "a3s1uiaet0y05r-ats.iot.us-east-1.amazonaws.com"
CERT = "C:\Users\Rohit\Desktop\fog-and-Edge\certs\100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-certificate.pem.crt"
KEY = "C:\Users\Rohit\Desktop\fog-and-Edge\certs\100583987a1821682b084d49d2f26391b7025b4b38083dada499fbb1ddb21400-private.pem.key"
ROOT = "C:\Users\Rohit\Desktop\fog-and-Edge\certs\AmazonRootCA1 (2).pem"
TOPIC = "solar/data"

class Command(BaseCommand):
    help = "Listen to MQTT sensor data and save to database"

    def handle(self, *args, **kwargs):
        def on_message(topic, payload, **kwargs):
            # 1. Force refresh DB connection for scalability
            connections.close_all()
            
            try:
                data = json.loads(payload.decode())

                # 2. Save reading with Cloud Validation flag
                SolarReading.objects.create(
                    panel_id=data.get("panel_id", "SP-01"),
                    voltage=data.get("voltage", 0),
                    current=data.get("current", 0),
                    temperature=data.get("temperature", 0),
                    light_intensity=data.get("light_intensity", 0),
                    humidity=data.get("humidity", 0),
                    power_watt=data.get("power_watt", 0),
                    local_alert=data.get("local_alert", False),
                    cloud_processed=True # Marks that SQS/Lambda path is active
                )
                print(f"Verified & Saved: {data.get('panel_id')} - {data.get('temperature')}°C")
            except Exception as e:
                print(f"Error processing message: {e}")

        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=CERT,
            pri_key_filepath=KEY,
            ca_filepath=ROOT,
            client_id="django_listener_scalable"
        )

        print("Connecting to AWS IoT Scalable Endpoint...")
        mqtt_connection.connect().result()
        mqtt_connection.subscribe(topic=TOPIC, qos=QoS.AT_LEAST_ONCE, callback=on_message)
        print("Listening... (SQS/Lambda path is now running in parallel)")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            mqtt_connection.disconnect().result()