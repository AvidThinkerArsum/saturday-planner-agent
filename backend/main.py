from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tools import search_candidate_places, filter_places_by_travel_time, rank_places

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExcursionRequest(BaseModel):
    starting_location: str
    max_travel_time: int
    place_keywords: str
    budget: str

@app.post("/plan")
def plan_excursion(request: ExcursionRequest):
    places = search_candidate_places.invoke(
        f"{request.starting_location} | {request.place_keywords}"
    )

    filtered = filter_places_by_travel_time(
        request.starting_location,
        places,
        request.max_travel_time
    )

    ranked = rank_places(filtered)

    return {
        "results": ranked
    }