import boto3
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
        # Paginating to get every single record in the table
        response = table.scan()
        items.extend(response.get('Items', []))
        
        # Keep scanning if there is a 'LastEvaluatedKey' (more data exists)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
    else:
        # Standard fetch for quick dashboard updates
        response = table.scan() # Returns up to 1MB of data
        items = response.get('Items', [])
    
    # 2. Sort by timestamp descending (newest first)
    items.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # 3. Clean and Process the top N items
    # Note: Even if we fetch 1000s, we only format the ones we display to save CPU
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
    # Pass fetch_all=True if you want the initial page load to consider everything
    readings = get_processed_items(limit=20, fetch_all=True)
    latest = readings[0] if readings else None
    return render(request, "monitor/dashboard.html", {"readings": readings, "latest": latest})

def latest_sensor_data(request):
    # Only need 1, so no need to fetch everything here (saves performance)
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
            "local_alert": latest.get("local_alert", False),
            "cloud_processed": latest.get("cloud_processed", True),
            "timestamp": latest.get("timestamp_str", "")
        }
    return JsonResponse(data)

def recent_readings(request):
    # Fetch all so the table shows the full history (up to your limit)
    readings = get_processed_items(limit=100, fetch_all=True)
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