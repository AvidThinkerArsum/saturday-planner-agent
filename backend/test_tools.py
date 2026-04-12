from tools import search_candidate_places, filter_places_by_travel_time, rank_places

# Step 1: search
places = search_candidate_places.invoke(
    "San Francisco | beach, park"
)

# Step 2: filter
filtered = filter_places_by_travel_time(
    "San Francisco",
    places,
    60
)

# Step 3: rank
ranked = rank_places(filtered)

print("\nRANKED RESULTS:\n")

for p in ranked:
    print(p["name"], "-", p["travel_time_minutes"], "mins")