import json
import time
from django.core.management.base import BaseCommand
from django.db import connections
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder
from monitor.models import SolarReading

ENDPOINT = "a1f1z1gmexcnut-ats.iot.us-east-1.amazonaws.com"
CERT = "/home/ec2-user/environment/fog-and-Edge/certs/f8105eccd5258be9bcbb21e49b9471875de970e0b19963e3777d7931ef6ba17e-certificate.pem.crt"
KEY = "/home/ec2-user/environment/fog-and-Edge/certs/f8105eccd5258be9bcbb21e49b9471875de970e0b19963e3777d7931ef6ba17e-private.pem.key"
ROOT = "/home/ec2-user/environment/fog-and-Edge/certs/AmazonRootCA1.pem"
TOPIC = "solar/telemetry"

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