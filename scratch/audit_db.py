import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotter_api.settings')
django.setup()

from fuel_route.models import FuelStation
from django.db import connection

print('--- DATA INTEGRITY ---')
total = FuelStation.objects.count()
null_coords = FuelStation.objects.filter(latitude__isnull=True).count()
zero_price = FuelStation.objects.filter(retail_price=0).count()
print(f'Total Stations: {total}')
print(f'Stations missing coordinates: {null_coords}')
print(f'Stations with $0 price: {zero_price}')

print('\n--- PERFORMANCE (INDEXES) ---')
with connection.cursor() as cursor:
    cursor.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'fuel_route_fuelstation';")
    indexes = cursor.fetchall()
    if not indexes:
        print("⚠️ No indexes found!")
    for idx in indexes:
        print(f"Found Index: {idx[0]}")

# Check if lat/lon are indexed
index_names = [idx[0] for idx in indexes]
if not any('latitude' in name.lower() for name in index_names):
    print("🚨 CRITICAL: No index on Latitude! Geolocation queries will be slow.")

print('\n--- DATA RANGE ---')
if total > 0:
    min_p = FuelStation.objects.order_by('retail_price').first().retail_price
    max_p = FuelStation.objects.order_by('-retail_price').first().retail_price
    print(f"Price Range: ${min_p} - ${max_p}")
