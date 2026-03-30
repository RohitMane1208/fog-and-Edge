import boto3 #boto
from django.shortcuts import render
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime

# Initialize DynamoDB Resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SolarData_Final')

def decimal_default(obj):
    """Helper to convert Decimal to float for JSON/Frontend compatibility"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def get_processed_items(limit=20, fetch_all=False):
    """
    Utility to fetch and clean items from DynamoDB.
    fetch_all=True will bypass the scan limit and pull the entire table.
    """
    items = []
    
    # 1. Fetching Logic
    if fetch_all:
        # to get every single record in the table
        response = table.scan()
        items.extend(response.get('Items', []))
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
    else:
        # Standard fetch for quick dashboard updates
        response = table.scan()
        items = response.get('Items', [])
    
    # 2. Sort by timestamp descending (newest first)
    items.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # 3. Process the top N items
    clean_items = []
    for item in items[:limit]:
        clean_item = {k: decimal_default(v) for k, v in item.items()}
        
        if 'timestamp' in clean_item:
            dt_object = datetime.fromtimestamp(clean_item['timestamp'])
            clean_item['timestamp_str'] = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            clean_item['time_only'] = dt_object.strftime("%H:%M:%S")
            
        clean_items.append(clean_item)
        
    return clean_items

def dashboard(request):
    readings = get_processed_items(limit=20, fetch_all=True)
    latest = readings[0] if readings else None
    return render(request, "monitor/dashboard.html", {"readings": readings, "latest": latest})

def latest_sensor_data(request):
    readings = get_processed_items(limit=1, fetch_all=False)
    if not readings:
        data = {"voltage": 0, "current": 0, "power_watt": 0, "temperature": 0, "local_alert": False, "cloud_processed": False}
    else:
        latest = readings[0]
        data = {
            "voltage": latest.get("voltage", 0),
            "current": latest.get("current", 0),
            "power_watt": latest.get("power_watt", 0),
            "temperature": latest.get("temperature", 0),
            "humidity": latest.get("humidity", 0),
            "light_intensity": latest.get("light_intensity", 0),
            "local_alert": latest.get("local_alert", False),
            "cloud_processed": latest.get("cloud_processed", True),
            "timestamp": latest.get("timestamp_str", "")
        }
    return JsonResponse(data)

def recent_readings(request):
    # Fetch all so the table shows the full history
    readings = get_processed_items(limit=100, fetch_all=True)
    data = []
    for r in readings:
        data.append({
            "voltage": r.get("voltage", 0),
            "power_watt": r.get("power_watt", 0),
            "temperature": r.get("temperature", 0),
            "humidity": r.get("humidity", 0),
            "light_intensity": r.get("light_intensity", 0),
            "local_alert": r.get("local_alert", False),
            "cloud_processed": r.get("cloud_processed", True),
            "timestamp": r.get("time_only", "")
        })
    return JsonResponse(data, safe=False)