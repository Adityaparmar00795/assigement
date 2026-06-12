from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="fuel_route_project")

address = "WOODSHED OF BIG CABIN, Big Cabin, OK, USA"

location = geolocator.geocode(address)

if location:
    print("Found!")
    print("Address:", location.address)
    print("Latitude:", location.latitude)
    print("Longitude:", location.longitude)
else:
    print("Location not found!")