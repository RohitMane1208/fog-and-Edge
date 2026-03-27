import json
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder
from monitor.models import SolarReading


TOPIC = "solar/telemetry"


def on_message(topic, payload, **kwargs):

    data = json.loads(payload.decode())

    SolarReading.objects.create(
        panel_id=data["panel_id"],
        voltage=data["voltage"],
        current=data["current"],
        temperature=data["temperature"],
        light_intensity=data["light_intensity"],
        humidity=data["humidity"],
        power_watt=data["power_watt"],
        local_alert=data["local_alert"]
    )

    print("Saved data")


mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint="YOUR_ENDPOINT",
    cert_filepath="cert.pem",
    pri_key_filepath="private.key",
    ca_filepath="root.pem",
    client_id="django-backend"
)

mqtt_connection.connect().result()

mqtt_connection.subscribe(
    topic=TOPIC,
    qos=QoS.AT_LEAST_ONCE,
    callback=on_message
)

print("Listening for solar data...")