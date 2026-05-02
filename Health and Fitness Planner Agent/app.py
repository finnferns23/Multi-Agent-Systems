"""Streamlit UI for the Health and Fitness Planner Agent."""

from __future__ import annotations

import os

from dotenv import load_dotenv
import streamlit as st

from agents import DEFAULT_GEMINI_MODEL, DEFAULT_OPENAI_MODEL, HealthFitnessOrchestrator
from tools import UserProfile, validate_profile

ACTIVITY_LEVELS = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]
DIETARY_OPTIONS = ["Balanced", "Vegetarian", "Vegan", "High Protein", "Low Carb", "Gluten Free", "Dairy Free", "Keto"]
FITNESS_GOALS = ["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training", "Mobility", "Body Recomposition"]
SEX_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]
EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]
STRESS_LEVELS = ["Low", "Moderate", "High"]
PROVIDERS = ["demo", "gemini", "openai"]


def init_state() -> None:
    st.session_state.setdefault("generated_plan", "")
    st.session_state.setdefault("qa_history", [])


def render_sidebar() -> tuple[str, str | None, str]:
    st.sidebar.header("Model Provider")
    provider = st.sidebar.selectbox("Provider", PROVIDERS, index=0)
    default_model = DEFAULT_OPENAI_MODEL if provider == "openai" else DEFAULT_GEMINI_MODEL if provider == "gemini" else "deterministic-demo"
    model_id = st.sidebar.text_input("Model ID", value=default_model)

    env_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("GEMINI_API_KEY", "")
    label = "OpenAI API Key" if provider == "openai" else "Gemini API Key"
    api_key = None
    if provider != "demo":
        api_key = st.sidebar.text_input(label, value=env_key or "", type="password")
        if api_key:
            st.sidebar.success(f"{provider.title()} key provided.")
        else:
            st.sidebar.warning("No API key provided. The app will use deterministic demo output.")
    else:
        st.sidebar.info("Demo mode runs locally without external API calls.")
    return provider, api_key, model_id


def collect_profile() -> UserProfile:
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=10, max_value=100, value=30, step=1)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
        activity_level = st.selectbox("Activity Level", ACTIVITY_LEVELS, index=2)
        dietary_preference = st.selectbox("Dietary Preference", DIETARY_OPTIONS)
        experience_level = st.selectbox("Training Experience", EXPERIENCE_LEVELS)
        sleep_hours = st.number_input("Typical Sleep (hours)", min_value=3.0, max_value=12.0, value=7.0, step=0.5)
    with col2:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
        sex = st.selectbox("Sex", SEX_OPTIONS, index=2)
        fitness_goal = st.selectbox("Fitness Goal", FITNESS_GOALS, index=3)
        available_days = st.slider("Training Days per Week", min_value=1, max_value=7, value=4)
        session_minutes = st.slider("Session Length (minutes)", min_value=10, max_value=180, value=45, step=5)
        stress_level = st.selectbox("Stress Level", STRESS_LEVELS, index=1)

    equipment = st.text_input("Equipment Access", value="Bodyweight and basic gym equipment")
    constraints = st.text_area("Constraints, injuries, allergies, schedule limits, or notes", value="None provided")

    return UserProfile(
        age=int(age),
        weight_kg=float(weight),
        height_cm=float(height),
        sex=sex,
        activity_level=activity_level,
        dietary_preference=dietary_preference,
        fitness_goal=fitness_goal,
        constraints=constraints.strip() or "None provided",
        experience_level=experience_level,
        available_days=int(available_days),
        session_minutes=int(session_minutes),
        equipment=equipment.strip() or "Not specified",
        sleep_hours=float(sleep_hours),
        stress_level=stress_level,
    )


def main() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    st.set_page_config(page_title="Health and Fitness Planner Agent", page_icon="🏋️", layout="wide")
    init_state()

    st.title("Health and Fitness Planner Agent")
    st.caption("Profile Analysis + Nutrition + Workout + Recovery + Safety Review agents")

    provider, api_key, model_id = render_sidebar()
    profile = collect_profile()
    errors = validate_profile(profile)

    if errors:
        for error in errors:
            st.error(error)
        return

    if st.button("Generate Personalized Plan", use_container_width=True):
        with st.spinner("Running the multi-agent planner..."):
            try:
                effective_provider = provider if api_key or provider == "demo" else "demo"
                orchestrator = HealthFitnessOrchestrator(
                    provider=effective_provider,
                    api_key=api_key,
                    model_id=model_id if provider != "demo" else None,
                )
                st.session_state.generated_plan = orchestrator.generate_plan(profile)
                st.session_state.qa_history = []
            except Exception as exc:
                st.error(f"Could not generate plan: {exc}")

    if st.session_state.generated_plan:
        st.markdown(st.session_state.generated_plan)
        st.download_button(
            "Download Plan as Markdown",
            data=st.session_state.generated_plan,
            file_name="health_fitness_plan.md",
            mime="text/markdown",
        )

        st.subheader("Ask a follow-up question")
        question = st.text_input("Question")
        if st.button("Get Answer") and question.strip():
            with st.spinner("Answering from the generated plan..."):
                effective_provider = provider if api_key or provider == "demo" else "demo"
                orchestrator = HealthFitnessOrchestrator(
                    provider=effective_provider,
                    api_key=api_key,
                    model_id=model_id if provider != "demo" else None,
                )
                answer = orchestrator.answer_question(question.strip(), st.session_state.generated_plan)
                st.session_state.qa_history.append((question.strip(), answer))

        for asked, answer in st.session_state.qa_history:
            st.markdown(f"**Q:** {asked}")
            st.markdown(f"**A:** {answer}")


if __name__ == "__main__":
    main()
