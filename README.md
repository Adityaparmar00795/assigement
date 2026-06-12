# Fuel Route Optimization API

## Overview
A Django REST API that calculates an optimal fuel plan between two US locations.

## Features
- Dynamic start/end locations.
- OpenRouteService integration.
- Route distance calculation.
- Fuel consumption estimation (10 MPG).
- 500-mile vehicle range handling.
- Fuel price optimization using the provided OPIS dataset.
- Recommended fuel stop selection.

## Tech Stack
- Django 5
- Django REST Framework
- SQLite
- Pandas
- OpenRouteService API
- Python Requests

## Assumptions
- Vehicle starts with a full tank.
- Maximum range: 500 miles.
- Fuel economy: 10 MPG.
- The supplied OPIS dataset does not contain geographic coordinates. Therefore, the implementation uses the provided pricing dataset and a heuristic-based fuel stop recommendation approach. The architecture allows future enrichment of station coordinates without changing the API contract.

## API Endpoint

POST /api/route/

Example Request:
{
    "start": "Dallas, TX",
    "finish": "Chicago, IL"
}

Example Response:
...
