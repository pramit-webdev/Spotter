import csv
import time
from django.core.management.base import BaseCommand
from fuel_route.models import FuelStation
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class Command(BaseCommand):
    help = 'Import fuel stations from CSV and geocode them'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='fuel-prices-for-be-assessment.csv', help='Path to the CSV file')
        parser.add_argument('--limit', type=int, default=100, help='Limit number of geocodings to avoid rate limits')

    def handle(self, *args, **options):
        file_path = options['file']
        limit = options['limit']
        geocoder = Nominatim(user_agent="fuel_route_planner")
        
        count = 0
        geocoded_count = 0

        with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Get or create station
                station, created = FuelStation.objects.get_or_create(
                    opis_id=row['OPIS Truckstop ID'],
                    defaults={
                        'name': row['Truckstop Name'],
                        'address': row['Address'],
                        'city': row['City'],
                        'state': row['State'],
                        'rack_id': row['Rack ID'],
                        'retail_price': row['Retail Price'],
                    }
                )

                # Geocode if missing and under limit
                if not station.latitude and geocoded_count < limit:
                    # Try different address formats
                    address_variants = [
                        f"{station.address}, {station.city}, {station.state}, USA",
                        f"{station.city}, {station.state}, USA" # Fallback to city/state
                    ]
                    
                    for addr in address_variants:
                        self.stdout.write(f"Geocoding: {addr}")
                        try:
                            location = geocoder.geocode(addr, timeout=10)
                            if location:
                                station.latitude = location.latitude
                                station.longitude = location.longitude
                                station.save()
                                geocoded_count += 1
                                self.stdout.write(self.style.SUCCESS(f"Success: {addr}"))
                                time.sleep(1) # Respect Nominatim rate limit
                                break
                            else:
                                self.stdout.write(self.style.WARNING(f"Failed: {addr}"))
                        except GeocoderTimedOut:
                            self.stdout.write(self.style.ERROR(f"Timeout: {addr}"))
                
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Finished. Processed {count} stations. Geocoded {geocoded_count} new stations."))
