from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
import requests
import geopandas as gpd
from shapely.geometry import Point

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (fine for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

wind_map = gpd.read_file("wind_zones_france.geojson")

WIND_SPEEDS = {
    1: 22,
    2: 24,
    3: 26,
    4: 28
}

def geocode(address):
    url = f"https://api-adresse.data.gouv.fr/search/?q={address}"
    r = requests.get(url).json()

    if not r["features"]:
        return None

    lon, lat = r["features"][0]["geometry"]["coordinates"]
    return lon, lat

def get_zone(lon, lat):
    point = Point(lon, lat)

    for _, row in wind_map.iterrows():
        if row.geometry.contains(point):
            return int(row["zone"])

    return None

def compute_pressure(vb):
    return 0.613 * vb**2

@app.get("/")
def root():
    return {"status": "Wind API running"}

@app.get("/calculate")
def calculate(address: str):
    coords = geocode(address)

    if not coords:
        return {"error": "Address not found"}

    lon, lat = coords
    zone = get_zone(lon, lat)

    if not zone:
        return {"error": "Zone not found"}

    vb = WIND_SPEEDS[zone]
    qp = compute_pressure(vb)

    return {
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "zone": zone,
        "basic_wind_velocity_m_s": vb,
        "peak_velocity_pressure_N_m2": round(qp, 1)
    }

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
