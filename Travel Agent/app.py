"""Streamlit UI for the multi-agent travel planner."""

from __future__ import annotations

import os
from datetime import date

import streamlit as st
from dotenv import load_dotenv

from agents import (
    APP_TITLE,
    ItineraryCoordinatorAgent,
    Settings,
    TripRequest,
    build_model,
    generate_ics,
    run_specialist_agents,
)

load_dotenv()


def load_settings_from_environment() -> Settings:
    """Load default app settings from environment variables."""
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        serpapi_api_key=os.getenv("SERPAPI_API_KEY", ""),
        google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY", ""),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    )


def reset_state() -> None:
    """Clear generated output from Streamlit session state."""
    st.session_state.final_plan = ""
    st.session_state.research_pack = ""


def render_sidebar(base_settings: Settings) -> tuple[str, Settings]:
    """Render model and API controls and return selected settings."""
    with st.sidebar:
        st.header("Model and API Settings")
        provider = st.selectbox("Planner model provider", ["OpenAI", "Ollama local"], index=0)
        openai_api_key = st.text_input("OpenAI API key", value=base_settings.openai_api_key, type="password")
        openai_model = st.text_input("OpenAI model", value=base_settings.openai_model)
        ollama_base_url = st.text_input("Ollama base URL", value=base_settings.ollama_base_url)
        ollama_model = st.text_input("Ollama model", value=base_settings.ollama_model)
        serpapi_key = st.text_input("SerpAPI key for live research", value=base_settings.serpapi_api_key, type="password")
        google_maps_key = st.text_input("Google Maps API key for route estimates", value=base_settings.google_maps_api_key, type="password")

        st.divider()
        st.write(
            "Optional keys improve live accuracy. Without them, the app still runs and clearly marks items that need verification."
        )
        if st.button("Reset results"):
            reset_state()
            st.rerun()

    settings = Settings(
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        serpapi_api_key=serpapi_key,
        google_maps_api_key=google_maps_key,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
    )
    return provider, settings


def render_trip_form() -> tuple[TripRequest | None, bool]:
    """Render trip inputs and return a TripRequest when submitted."""
    st.subheader("Trip Details")
    left, right = st.columns(2)

    with left:
        destination = st.text_input("Destination", placeholder="e.g., Muscat, Tokyo, Paris")
        origin = st.text_input("Origin / starting city", placeholder="e.g., Muscat, Mumbai, London")
        start_date = st.date_input("Start date", value=date.today())
        days = st.number_input("Number of days", min_value=1, max_value=30, value=5, step=1)

    with right:
        budget = st.text_input("Budget", placeholder="e.g., USD 1500 total, budget-friendly, luxury")
        travelers = st.text_input("Travelers", placeholder="e.g., solo, couple, family of 4")
        pace = st.selectbox("Travel pace", ["Relaxed", "Balanced", "Packed"], index=1)
        accommodation_style = st.selectbox(
            "Accommodation style",
            ["Flexible", "Budget", "Mid-range", "Luxury", "Apartment / serviced stay"],
            index=0,
        )

    preferences = st.text_area(
        "Preferences",
        placeholder="Food, culture, beaches, shopping, nightlife, nature, child-friendly, photography, etc.",
    )
    accessibility = st.text_area(
        "Accessibility / special requirements",
        placeholder="Low walking, wheelchair access, screen-reader friendly planning, dietary needs, etc.",
    )
    show_research = st.checkbox("Show specialist-agent research pack", value=False)

    submitted = st.button("Generate Travel Plan", type="primary")
    if not submitted:
        return None, show_research

    if not destination.strip():
        st.error("Please enter a destination.")
        return None, show_research

    request = TripRequest(
        destination=destination.strip(),
        days=int(days),
        start_date=start_date,
        origin=origin.strip(),
        budget=budget.strip(),
        travelers=travelers.strip(),
        preferences=preferences.strip(),
        accessibility=accessibility.strip(),
        pace=pace,
        accommodation_style=accommodation_style,
    )
    return request, show_research


def generate_plan(request: TripRequest, provider: str, settings: Settings) -> None:
    """Run specialist agents and coordinate the final itinerary."""
    with st.spinner("Running MCP tools and specialist travel agents..."):
        research_pack = run_specialist_agents(request, settings)
        st.session_state.research_pack = research_pack

    try:
        with st.spinner("Coordinating final itinerary..."):
            model = build_model(provider, settings)
            final_plan = ItineraryCoordinatorAgent(model).run(request, research_pack)
            st.session_state.final_plan = final_plan
            st.session_state.last_start_date = request.start_date.isoformat()
            st.session_state.last_days = request.days
        st.success("Travel plan generated successfully.")
    except Exception as exc:
        st.session_state.final_plan = ""
        st.error(f"Final planner failed: {exc}")
        st.info("Check model/API settings. Ollama mode requires a running local Ollama server and a pulled model.")


def render_results(show_research: bool) -> None:
    """Display final itinerary, downloads, and optional research pack."""
    if st.session_state.final_plan:
        st.subheader("Final Travel Plan")
        st.markdown(st.session_state.final_plan)
        st.download_button(
            "Download itinerary as Markdown",
            data=st.session_state.final_plan,
            file_name="travel_plan.md",
            mime="text/markdown",
        )

        stored_start = date.fromisoformat(st.session_state.last_start_date)
        stored_days = int(st.session_state.last_days)
        st.download_button(
            "Download calendar file (.ics)",
            data=generate_ics(st.session_state.final_plan, stored_start, stored_days),
            file_name="travel_itinerary.ics",
            mime="text/calendar",
        )

    if show_research and st.session_state.research_pack:
        st.subheader("Specialist-Agent Research Pack")
        st.markdown(st.session_state.research_pack)


def render_app() -> None:
    """Main Streamlit application entry point."""
    st.set_page_config(page_title=APP_TITLE, page_icon="✈️", layout="wide")

    for key, default in {
        "final_plan": "",
        "research_pack": "",
        "last_start_date": date.today().isoformat(),
        "last_days": 1,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    st.title("✈️ Multi-Agent AI Travel Agent")
    st.caption("Travel agent, travel planner, and MCP-style tool workflow in a clean modular Streamlit project.")

    provider, settings = render_sidebar(load_settings_from_environment())
    request, show_research = render_trip_form()
    if request is not None:
        generate_plan(request, provider, settings)
    render_results(show_research)


if __name__ == "__main__":
    render_app()
