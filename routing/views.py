from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings
from django.db import models
from routing.models import FuelStation

import requests


def geocode_location(location_name):
    """
    Convert a place name like 'Dallas, TX'
    into [longitude, latitude].
    """
    url = "https://api.openrouteservice.org/geocode/search"

    headers = {
        "Authorization": settings.ORS_API_KEY
    }

    params = {
        "text": location_name,
        "size": 1
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    features = data.get("features", [])
    if not features:
        return None

    return features[0]["geometry"]["coordinates"]


@api_view(["POST"])
def route_optimizer(request):
    start = request.data.get("start")
    finish = request.data.get("finish")

    if not start or not finish:
        return Response(
            {
                "error": "Please provide both 'start' and 'finish'."
            },
            status=400
        )

    # Convert locations to coordinates
    start_coords = geocode_location(start)
    finish_coords = geocode_location(finish)

    if not start_coords or not finish_coords:
        return Response(
            {
                "error": "Could not find one or both locations."
            },
            status=400
        )

    # Call OpenRouteService Directions API
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            start_coords,
            finish_coords
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    if response.status_code != 200:
        return Response(
            {
                "error": "Failed to retrieve route information.",
                "details": data
            },
            status=500
        )

    # Route information
    distance_meters = data["routes"][0]["summary"]["distance"]
    distance_miles = round(distance_meters / 1609.34, 2)
    route_geometry = data["routes"][0]["geometry"]

    # Vehicle assumptions
    MPG = 10
    MAX_RANGE = 500

    gallons_needed = round(distance_miles / MPG, 2)

    # Assume vehicle starts with a full tank
    fuel_stops_needed = max(0, int(distance_miles // MAX_RANGE))

    # Average fuel price across dataset
    avg_price = FuelStation.objects.aggregate(
        avg_price=models.Avg("retail_price")
    )["avg_price"]

    estimated_fuel_cost = round(gallons_needed * avg_price, 2)

    # Pick cheapest stations (heuristic approach)
    cheapest_stations = FuelStation.objects.order_by(
        "retail_price"
    )[:max(1, fuel_stops_needed)]

    fuel_stop_list = []

    for station in cheapest_stations:
        fuel_stop_list.append({
            "truckstop_name": station.truckstop_name,
            "city": station.city,
            "state": station.state,
            "retail_price": round(station.retail_price, 3)
        })

    # Create Google Maps URL
    origin = start.replace(" ", "+")
    destination = finish.replace(" ", "+")

    map_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&travelmode=driving"
    )

    # Add recommended fuel stops as waypoints
    waypoints = []

    for station in fuel_stop_list:
        city = station["city"].replace(" ", "+")
        state = station["state"]
        waypoints.append(f"{city},{state}")

    if waypoints:
        map_url += "&waypoints=" + "|".join(waypoints)

    # Final API response
    return Response({
        "start": start,
        "finish": finish,
        "distance_miles": distance_miles,
        "gallons_needed": gallons_needed,
        "fuel_stops_needed": fuel_stops_needed,
        "estimated_fuel_cost": estimated_fuel_cost,
        "recommended_fuel_stops": fuel_stop_list,
        "google_maps_url": map_url,
        "route_geometry": route_geometry,
        
    })
