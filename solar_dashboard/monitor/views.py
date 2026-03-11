from django.shortcuts import render
from django.http import JsonResponse
from .models import SolarReading

def dashboard(request):
    readings = SolarReading.objects.all()[:20]
    latest = readings.first() if readings.exists() else None
    return render(request, "monitor/dashboard.html", {"readings": readings, "latest": latest})

def latest_sensor_data(request):
    latest = SolarReading.objects.order_by('-timestamp').first()
    if latest is None:
        data = {"voltage": 0, "current": 0, "power_watt": 0, "temperature": 0, "local_alert": False, "cloud_processed": False}
    else:
        data = {
            "voltage": latest.voltage,
            "current": latest.current,
            "power_watt": latest.power_watt,
            "temperature": latest.temperature,
            "local_alert": latest.local_alert,
            "cloud_processed": latest.cloud_processed, # Scalability flag
            "timestamp": latest.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
    return JsonResponse(data)

def recent_readings(request):
    readings = SolarReading.objects.order_by('-timestamp')[:20]
    data = []
    for r in readings:
        data.append({
            "id": r.id,
            "voltage": r.voltage,
            "current": r.current,
            "power_watt": r.power_watt,
            "temperature": r.temperature,
            "local_alert": r.local_alert,
            "cloud_processed": r.cloud_processed, # Scalability flag
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return JsonResponse(data, safe=False)