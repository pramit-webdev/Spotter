import requests
import json
import math
import os
from .models import FuelStation
from django.db.models import Q

class RoutingService:
    @staticmethod
    def get_route(start_coords, end_coords):
        """
        Get route from OpenRouteService. coords are [lon, lat]
        """
        api_key = os.getenv('ORS_API_KEY')
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        headers = {
            'Accept': 'application/json, application/geo+json',
            'Authorization': api_key,
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        body = {"coordinates": [start_coords, end_coords]}
        
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code != 200:
            error_data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            raise Exception(f"ORS API Error ({response.status_code}): {error_data}")
            
        return response.json()

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in miles"""
        R = 3958.8  # Earth radius in miles
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

    @staticmethod
    def find_optimal_stops(route_geojson):
        """
        Implements greedy fuel optimization.
        """
        try:
            if not route_geojson.get('routes'):
                return []
                
            line_points = route_geojson['routes'][0]['geometry']['coordinates']
            summary = route_geojson['routes'][0]['summary']
            total_dist_miles = summary['distance'] * 0.000621371
            
            # 1. Get candidate stations within a bounding box of the route
            lats = [p[1] for p in line_points]
            lons = [p[0] for p in line_points]
            stations = FuelStation.objects.filter(
                latitude__range=(min(lats)-0.1, max(lats)+0.1),
                longitude__range=(min(lons)-0.1, max(lons)+0.1)
            )
            
            selected_stops = []
            miles_traveled = 0
            
            # Greedy logic
            while miles_traveled < (total_dist_miles - 100):
                candidates = [s for s in stations if s not in selected_stops]
                if not candidates:
                    break
                    
                best_station = min(candidates, key=lambda x: x.retail_price)
                selected_stops.append(best_station)
                miles_traveled += 450
                
            return selected_stops
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected route data format: {str(e)}")
