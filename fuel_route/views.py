from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FuelStation
from .serializers import FuelStationSerializer
from .services import RoutingService
from geopy.geocoders import ArcGIS
import json

class FuelRouteView(APIView):
    def get(self, request):
        start_loc = request.query_params.get('start')
        end_loc = request.query_params.get('end')
        format_type = request.query_params.get('format', 'json')
        
        if not start_loc or not end_loc:
            return Response({"error": "Start and end locations are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # ArcGIS Geocoder is much more stable on shared hosting like Render
            geocoder = ArcGIS(user_agent="fuel_route_planner_v2")
            
            start_geo = geocoder.geocode(start_loc, timeout=10)
            end_geo = geocoder.geocode(end_loc, timeout=10)
            
            if not start_geo or not end_geo:
                return Response({"error": f"Could not geocode locations. Start: {start_geo}, End: {end_geo}"}, status=status.HTTP_400_BAD_REQUEST)
            
            start_coords = [start_geo.longitude, start_geo.latitude]
            end_coords = [end_geo.longitude, end_geo.latitude]
            
            # Get Route from OSRM
            route = RoutingService.get_route(start_coords, end_coords)
            stops = RoutingService.find_optimal_stops(route)
            serializer = FuelStationSerializer(stops, many=True)
            
            # Calculations
            total_dist_meters = route['routes'][0].get('distance', 0)
            total_dist_miles = total_dist_meters * 0.000621371
            total_fuel_needed = total_dist_miles / 10.0
            avg_price = sum([float(s.retail_price) for s in stops]) / len(stops) if stops else 0
            total_cost = float(total_fuel_needed) * float(avg_price)
            
            data = {
                "start": start_loc,
                "end": end_loc,
                "route": route,
                "fuel_stops": serializer.data,
                "summary": {
                    "total_distance_miles": round(total_dist_miles, 2),
                    "total_fuel_gallons": round(total_fuel_needed, 2),
                    "estimated_total_cost": round(total_cost, 2)
                }
            }

            if format_type == 'map':
                return render(request, 'fuel_route/map.html', {
                    **data,
                    'route_json': json.dumps(route),
                    'stops_json': json.dumps(serializer.data)
                })
            
            return Response(data)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
