from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import FuelStation

class FuelRouteE2ETest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a mock station in Arizona for testing
        FuelStation.objects.create(
            opis_id=9999,
            name="Test Stop",
            address="123 Test St",
            city="Eloy",
            state="AZ",
            rack_id=1,
            retail_price=3.10,
            latitude=32.756,
            longitude=-111.554
        )

    def test_route_json_success(self):
        """Test a standard route request returns valid JSON data"""
        url = reverse('fuel-route')
        response = self.client.get(url, {'start': 'Phoenix,AZ', 'end': 'Tucson,AZ', 'format': 'json'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('route', response.data)
        self.assertIn('fuel_stops', response.data)
        self.assertIn('summary', response.data)
        self.assertTrue(response.data['summary']['total_distance_miles'] > 0)

    def test_route_map_success(self):
        """Test that format=map returns an HTML page"""
        url = reverse('fuel-route')
        response = self.client.get(url, {'start': 'Phoenix,AZ', 'end': 'Tucson,AZ', 'format': 'map'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.assertContains(response, 'id="map"') # Check if map div exists

    def test_missing_params(self):
        """Test that missing start/end returns 400"""
        url = reverse('fuel-route')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_location(self):
        """Test that a non-existent location is handled gracefully"""
        url = reverse('fuel-route')
        response = self.client.get(url, {'start': 'NowhereCity12345', 'end': 'Tucson,AZ'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
