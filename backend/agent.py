from dataclasses import dataclass, field
from typing import List

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model

from tools import (
    search_candidate_places,
    get_travel_time,
    get_weather_and_best_time,
    estimate_budget_and_vibe,
    rank_places,
)

SYSTEM_PROMPT = """
You are a Saturday excursion planning agent.

Your job is to help the user find good excursion options based on:
- starting location
- maximum one-way travel time
- place keywords
- budget level

You MUST follow this process in order:

1. Use search_candidate_places to find candidate places based on the user's location and keywords.
2. Use get_travel_time to check one-way travel time for candidate places using public-transit-compatible travel only.
3. Public-transit-compatible travel may include a mix of walking, bus, and train.
4. Remove any places that exceed the user's maximum travel time.
5. Use get_weather_and_best_time for the remaining places.
6. Use estimate_budget_and_vibe for the remaining places.
7. Use rank_places to rank the final places.

Rules:
- Do not skip steps.
- Do not invent places that were not returned by the search tool.
- Do not include places above the allowed travel time.
- Travel must be based only on walking, bus, and train.
- Never assume private car, Uber, Lyft, taxi, or any other private transport.
- Always return multiple ranked options when possible.
- If only a few valid places remain, return them and explain that the constraints limited the results.
- Be concrete and practical.
- Keep explanations short but useful.
"""


@dataclass
class PlaceResult:
    name: str
    score: float
    travel_time_minutes: int
    best_time_to_visit: str
    budget: str
    vibe: str
    top_things_to_enjoy: List[str] = field(default_factory=list)
    why_it_matched: str = ""


@dataclass
class ExcursionResponse:
    recommendations: List[PlaceResult]


model = init_chat_model(
    "gpt-4o-mini",
    temperature=0,
)


agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        search_candidate_places,
        get_travel_time,
        get_weather_and_best_time,
        estimate_budget_and_vibe,
        rank_places,
    ],
    response_format=ToolStrategy(ExcursionResponse),
)


def run_excursion_agent(user_input: str):
    """
    Runs the excursion planning agent.
    user_input should be a fully formatted string containing all required fields.
    """
    response = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }
    )

    return response["structured_response"]