from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings
import requests


@api_view(["POST"])
def route_optimizer(request):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json"
    }

    # Hardcoded for now (Dallas -> Chicago)
    body = {
        "coordinates": [
            [-96.7970, 32.7767],
            [-87.6298, 41.8781]
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    distance_meters = data["routes"][0]["summary"]["distance"]
    distance_miles = round(distance_meters / 1609.34, 2)

    return Response({
        "start": "Dallas, TX",
        "finish": "Chicago, IL",
        "distance_miles": distance_miles
    })