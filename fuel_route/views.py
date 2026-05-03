from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FuelStation
from .serializers import FuelStationSerializer
from .services import RoutingService
from geopy.geocoders import Nominatim
import json

class FuelRouteView(APIView):
    def get(self, request):
        start_loc = request.query_params.get('start')
        end_loc = request.query_params.get('end')
        format_type = request.query_params.get('format', 'json')
        
        if not start_loc or not end_loc:
            return Response({"error": "Start and end locations are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Geocode
            geocoder = Nominatim(user_agent="fuel_route_planner")
            start_geo = geocoder.geocode(start_loc)
            end_geo = geocoder.geocode(end_loc)
            
            if not start_geo or not end_geo:
                return Response({
                    "error": f"Could not geocode locations. Start: {start_geo}, End: {end_geo}",
                    "start_query": start_loc,
                    "end_query": end_loc
                }, status=status.HTTP_400_BAD_REQUEST)
            
            start_coords = [start_geo.longitude, start_geo.latitude]
            end_coords = [end_geo.longitude, end_geo.latitude]
            
            # Get Route
            route = RoutingService.get_route(start_coords, end_coords)
            
            # Find Stops
            stops = RoutingService.find_optimal_stops(route)
            serializer = FuelStationSerializer(stops, many=True)
            
            # Calculations
            summary_data = route['routes'][0]['summary']
            total_dist_miles = summary_data['distance'] * 0.000621371
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
            # Catch all errors and return them as JSON for easier debugging
            return Response({
                "error": str(e),
                "details": "Check your ORS_API_KEY and Ensure geocoding is working."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
