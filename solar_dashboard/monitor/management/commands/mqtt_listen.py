import json
import time
from django.core.management.base import BaseCommand
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder
from monitor.models import SolarReading

ENDPOINT = "a1e55si5y6nep5-ats.iot.us-east-1.amazonaws.com"

CERT = "/home/ec2-user/environment/smart_solar_farm/certs/bada0bc5236e5e5252cdf606acbd8ad77a794cd50e489ec7c27f10edca69ab11-certificate.pem.crt"
KEY = "/home/ec2-user/environment/smart_solar_farm/certs/bada0bc5236e5e5252cdf606acbd8ad77a794cd50e489ec7c27f10edca69ab11-private.pem.key"
ROOT = "/home/ec2-user/environment/smart_solar_farm/certs/AmazonRootCA1.pem"

TOPIC = "solar/telemetry"


class Command(BaseCommand):

    help = "Listen to MQTT sensor data and save to database"

    def handle(self, *args, **kwargs):

        def on_message(topic, payload, **kwargs):
            """Callback for incoming MQTT messages"""
            data = json.loads(payload.decode())

            # Save new reading to database
            SolarReading.objects.create(
                panel_id=data.get("panel_id", 1),
                voltage=data.get("voltage", 0),
                current=data.get("current", 0),
                temperature=data.get("temperature", 0),
                light_intensity=data.get("light_intensity", 0),
                humidity=data.get("humidity", 0),
                power_watt=data.get("power_watt", 0),
                local_alert=data.get("local_alert", False)
            )

            # Optional: print for debugging
            print("Saved sensor reading:", data)

        # Build MQTT connection
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=CERT,
            pri_key_filepath=KEY,
            ca_filepath=ROOT,
            client_id="django_listener"
        )

        print("Connecting to AWS IoT...")
        mqtt_connection.connect().result()
        print("Connected.")

        # Subscribe to topic
        mqtt_connection.subscribe(
            topic=TOPIC,
            qos=QoS.AT_LEAST_ONCE,
            callback=on_message
        )

        print("Listening for sensor data... Press Ctrl+C to stop.")

        try:
            # Keep the command running
            while True:
                time.sleep(1)  # prevents CPU overload
        except KeyboardInterrupt:
            print("Stopping MQTT listener...")
            mqtt_connection.disconnect().result()