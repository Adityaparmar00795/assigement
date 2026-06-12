from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import models
from routing.models import FuelStation
from django.conf import settings
import requests


def geocode_location(location_name):
    """
    Convert a place name like 'Dallas, TX' into [longitude, latitude]
    using OpenRouteService geocoding.
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

    # ORS returns [longitude, latitude]
    return features[0]["geometry"]["coordinates"]


@api_view(["POST"])
def route_optimizer(request):
    start = request.data.get("start")
    finish = request.data.get("finish")

    if not start or not finish:
        return Response(
            {"error": "Please provide both 'start' and 'finish'."},
            status=400
        )

    # Convert city names to coordinates
    start_coords = geocode_location(start)
    finish_coords = geocode_location(finish)

    if not start_coords or not finish_coords:
        return Response(
            {"error": "Could not find one or both locations."},
            status=400
        )

    # Get driving route
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

    distance_meters = data["routes"][0]["summary"]["distance"]
    distance_miles = round(distance_meters / 1609.34, 2)

    route_geometry = data["routes"][0]["geometry"]

    # Vehicle assumptions
    MPG = 10
    MAX_RANGE = 500
    AVERAGE_TANK_SIZE = MAX_RANGE / MPG  # 50 gallons

    # Total fuel needed
    gallons_needed = round(distance_miles / MPG, 2)

    # Minimum number of refueling stops
    # (Assume vehicle starts with a full tank)
    fuel_stops_needed = max(0, int(distance_miles // MAX_RANGE))

    # Temporary estimate using average fuel price in dataset

    avg_price = FuelStation.objects.all().aggregate(
        avg_price=models.Avg("retail_price")
    )["avg_price"]

    estimated_fuel_cost = round(gallons_needed * avg_price, 2)

    # Select cheapest fuel stations
    cheapest_stations = FuelStation.objects.order_by(
        "retail_price")[:max(1, fuel_stops_needed)]

    fuel_stop_list = []

    for station in cheapest_stations:
        fuel_stop_list.append({
            "truckstop_name": station.truckstop_name,
            "city": station.city,
            "state": station.state,
            "retail_price": round(station.retail_price, 3)
        })

    return Response({
        "start": start,
        "finish": finish,
        "distance_miles": distance_miles,
        "gallons_needed": gallons_needed,
        "fuel_stops_needed": fuel_stops_needed,
        "estimated_fuel_cost": estimated_fuel_cost,
        "recommended_fuel_stops": fuel_stop_list,
        "route_geometry": route_geometry
    })
