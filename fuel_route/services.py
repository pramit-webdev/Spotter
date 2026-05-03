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
        Get route from OSRM (Open Source Routing Machine)
        Public demo server - No API key needed!
        coords are [lon, lat]
        """
        # OSRM format: lon,lat;lon,lat
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}?overview=full&geometries=geojson"
        
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"OSRM API Error ({response.status_code}): {response.text}")
            
        data = response.json()
        
        # Format OSRM response to match our expected structure
        # OSRM returns 'routes', we just need to make sure indexing works
        return data

    @staticmethod
    def find_optimal_stops(route_geojson):
        """
        Implements greedy fuel optimization.
        """
        try:
            if not route_geojson.get('routes'):
                return []
                
            line_points = route_geojson['routes'][0]['geometry']['coordinates']
            # OSRM summary uses 'distance' in meters, same as ORS
            summary = route_geojson['routes'][0]
            total_dist_meters = summary.get('distance', 0)
            total_dist_miles = total_dist_meters * 0.000621371
            
            # 1. Get candidate stations near the route
            lats = [p[1] for p in line_points]
            lons = [p[0] for p in line_points]
            stations = FuelStation.objects.filter(
                latitude__range=(min(lats)-0.1, max(lats)+0.1),
                longitude__range=(min(lons)-0.1, max(lons)+0.1)
            )
            
            selected_stops = []
            miles_traveled = 0
            
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
