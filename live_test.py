import requests

LIVE_URL = "https://spotter-jmm5.onrender.com/api/route/"

def run_e2e_test():
    print("🌍 Starting Live Production E2E Test...")
    
    # 1. Test JSON Response
    print("🔍 Testing JSON API...")
    params = {'start': 'Phoenix,AZ', 'end': 'Tucson,AZ', 'format': 'json'}
    response = requests.get(LIVE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ JSON Success: Route is {data['summary']['total_distance_miles']} miles.")
        print(f"✅ JSON Success: Found {len(data['fuel_stops'])} fuel stops.")
    else:
        print(f"❌ JSON Failed: Status {response.status_code}")
        print(response.text)

    # 2. Test Map Response
    print("\n🗺️ Testing Map View...")
    params['ui'] = 'map'
    response = requests.get(LIVE_URL, params=params)
    
    if response.status_code == 200 and '<div id="map"' in response.text:
        print("✅ Map Success: HTML rendered with Leaflet map container.")
    else:
        print(f"❌ Map Failed: Status {response.status_code}")

    print("\n🏁 LIVE E2E TEST COMPLETE!")

if __name__ == "__main__":
    run_e2e_test()
