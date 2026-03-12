import boto3
from django.shortcuts import render
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime

# Initialize DynamoDB Resource
# In AWS Academy/Elastic Beanstalk, it uses the environment's IAM Role automatically
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SolarData_New')

def decimal_default(obj):
    """Helper to convert Decimal to float for JSON/Frontend compatibility"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def get_processed_items(limit=20):
    """Utility to fetch and clean items from DynamoDB"""
    response = table.scan(Limit=50) # Scan slightly more to ensure we have enough after sorting
    items = response.get('Items', [])
    
    # Sort by timestamp descending (newest first)
    items.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # Take the top N and clean Decimal types
    clean_items = []
    for item in items[:limit]:
        clean_item = {k: decimal_default(v) for k, v in item.items()}
        
        # Format the timestamp for the frontend (convert epoch to readable string)
        if 'timestamp' in clean_item:
            dt_object = datetime.fromtimestamp(clean_item['timestamp'])
            clean_item['timestamp_str'] = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            clean_item['time_only'] = dt_object.strftime("%H:%M:%S")
            
        clean_items.append(clean_item)
    return clean_items

def dashboard(request):
    readings = get_processed_items(20)
    latest = readings[0] if readings else None
    return render(request, "monitor/dashboard.html", {"readings": readings, "latest": latest})

def latest_sensor_data(request):
    readings = get_processed_items(1)
    if not readings:
        data = {"voltage": 0, "current": 0, "power_watt": 0, "temperature": 0, "local_alert": False, "cloud_processed": False}
    else:
        latest = readings[0]
        data = {
            "voltage": latest.get("voltage", 0),
            "current": latest.get("current", 0),
            "power_watt": latest.get("power_watt", 0),
            "temperature": latest.get("temperature", 0),
            "local_alert": latest.get("local_alert", False),
            "cloud_processed": latest.get("cloud_processed", True),
            "timestamp": latest.get("timestamp_str", "")
        }
    return JsonResponse(data)

def recent_readings(request):
    readings = get_processed_items(20)
    # We map the internal names to the keys your JS expects
    data = []
    for r in readings:
        data.append({
            "voltage": r.get("voltage", 0),
            "power_watt": r.get("power_watt", 0),
            "temperature": r.get("temperature", 0),
            "local_alert": r.get("local_alert", False),
            "cloud_processed": r.get("cloud_processed", True),
            "timestamp": r.get("time_only", "")
        })
    return JsonResponse(data, safe=False)