import requests
import os
from langchain.tools import tool

GOOGLE_API_KEY = "AIzaSyDa9RmVcUMZE99eT2_TQKwKACx8BC4Uevw"

@tool
def search_candidate_places(input_str: str):
    """
    Finds places based on starting location and keywords.
    
    Input format:
    "starting_location | keyword1, keyword2"
    
    Example:
    "San Francisco | beach, park"
    """

    try:
        location, keywords_str = input_str.split("|")
        location = location.strip()
        keywords = [k.strip() for k in keywords_str.split(",")]
    except:
        return "Invalid input format. Use: 'location | keyword1, keyword2'"

    results = []

    for keyword in keywords:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{keyword} near {location}",
            "format": "json",
            "limit": 5
        }

        response = requests.get(url, params=params, headers={
            "User-Agent": "saturday-planner-agent"
        })

        data = response.json()

        for place in data:
            results.append({
                "name": place.get("display_name"),
                "lat": place.get("lat"),
                "lon": place.get("lon"),
                "type": place.get("type")
            })

    return results[:15]  # limit total candidates


@tool
def get_travel_time(input_str: str):
    """
    Gets travel time using public transit.

    Input format:
    "starting_location | destination_lat, destination_lon"
    
    Example:
    "San Francisco | 37.76,-122.51"
    """

    try:
        start, dest = input_str.split("|")
        start = start.strip()
        lat, lon = dest.strip().split(",")
    except:
        return "Invalid input format"

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": start,
        "destination": f"{lat},{lon}",
        "mode": "transit",   # 🔥 key line
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    #print("DEBUG RESPONSE:", data)  # ✅ always safe here

    try:
        if data.get("routes"):
            duration = data["routes"][0]["legs"][0]["duration"]["value"]
            return duration // 60
        else:
            return None
    except:
        return None
    
def filter_places_by_travel_time(start_location: str, places: list, max_time: int):
    filtered = []

    for place in places:
        lat = place["lat"]
        lon = place["lon"]

        travel_time = get_travel_time.invoke(
            f"{start_location} | {lat},{lon}"
        )

        if travel_time is not None and travel_time <= max_time:
            place["travel_time_minutes"] = travel_time
            filtered.append(place)

    return filtered

def rank_places(places: list):
    return sorted(places, key=lambda x: x["travel_time_minutes"])