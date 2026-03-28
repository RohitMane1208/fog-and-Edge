def process_data(data):
    """
    Fog layer processing
    """

    voltage = data["voltage"]
    current = data["current"]

    power = voltage * current
    data["power_watt"] = round(power, 2)

    alert = False

    if data["temperature"] > 75:
        alert = True

    if data["light_intensity"] > 800 and power < 50:
        alert = True

    data["local_alert"] = alert

    return data