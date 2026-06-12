import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from routing.models import FuelStation

# Read CSV
df = pd.read_csv("data/fuel-prices-for-be-assessment.csv")

# Clear existing data (optional for now)
FuelStation.objects.all().delete()

count = 0

for _, row in df.iterrows():
    FuelStation.objects.create(
        opis_id=int(row["OPIS Truckstop ID"]),
        truckstop_name=row["Truckstop Name"],
        address=row["Address"],
        city=row["City"],
        state=row["State"],
        rack_id=int(row["Rack ID"]),
        retail_price=float(row["Retail Price"])
    )
    count += 1

print(f"Successfully imported {count} fuel stations!")