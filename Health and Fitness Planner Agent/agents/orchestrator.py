"""LangGraph orchestration for the Health and Fitness Planner Agent."""

from __future__ import annotations

from typing import Dict, Optional, TypedDict

from .base import AgentResult, DEFAULT_GEMINI_MODEL, DEFAULT_OPENAI_MODEL, SUPPORTED_PROVIDERS
from .nutrition_agent import NutritionPlanningAgent
from .meal_planner_agent import MealPlannerAgent
from .profile_agent import ProfileAnalysisAgent
from .qa_agent import FollowUpQAAgent
from .recovery_agent import RecoveryHabitAgent
from .safety_agent import SafetyReviewAgent
from .workout_agent import WorkoutProgrammingAgent
from tools import (
    UserProfile,
    build_safety_flags,
    calculate_bmi,
    estimate_daily_water_liters,
    format_plan,
    safety_notice,
)

try:
    from langgraph.graph import END, StateGraph
except ImportError:  # Keeps demo mode runnable before dependency installation.
    END = None
    StateGraph = None


class PlannerState(TypedDict, total=False):
    profile: UserProfile
    outputs: Dict[str, AgentResult]
    review: AgentResult
    final_plan: str


class HealthFitnessOrchestrator:
    """Coordinates specialist agents using LangGraph, with a safe fallback for demo validation."""

    def __init__(self, provider: str = "demo", api_key: Optional[str] = None, model_id: Optional[str] = None) -> None:
        provider = provider.lower().strip()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider '{provider}'. Use one of: {sorted(SUPPORTED_PROVIDERS)}")
        self.provider = provider
        self.api_key = api_key
        self.model_id = model_id
        self.profile_agent = ProfileAnalysisAgent(provider, api_key, model_id)
        self.nutrition_agent = NutritionPlanningAgent(provider, api_key, model_id)
        self.meal_planner_agent = MealPlannerAgent(provider, api_key, model_id)
        self.workout_agent = WorkoutProgrammingAgent(provider, api_key, model_id)
        self.recovery_agent = RecoveryHabitAgent(provider, api_key, model_id)
        self.safety_agent = SafetyReviewAgent(provider, api_key, model_id)
        self.qa_agent = FollowUpQAAgent(provider, api_key, model_id)
        self.effective_model_id = self.profile_agent.model_id

    def _profile_node(self, state: PlannerState) -> PlannerState:
        outputs = dict(state.get("outputs", {}))
        outputs["profile"] = self.profile_agent.analyze(state["profile"])
        return {**state, "outputs": outputs}

    def _nutrition_node(self, state: PlannerState) -> PlannerState:
        outputs = dict(state.get("outputs", {}))
        outputs["nutrition"] = self.nutrition_agent.create_plan(state["profile"])
        return {**state, "outputs": outputs}

    def _meal_planning_node(self, state: PlannerState) -> PlannerState:
        outputs = dict(state.get("outputs", {}))
        outputs["meal_planning"] = self.meal_planner_agent.create_plan(state["profile"])
        return {**state, "outputs": outputs}

    def _workout_node(self, state: PlannerState) -> PlannerState:
        outputs = dict(state.get("outputs", {}))
        outputs["workout"] = self.workout_agent.create_plan(state["profile"])
        return {**state, "outputs": outputs}

    def _recovery_node(self, state: PlannerState) -> PlannerState:
        outputs = dict(state.get("outputs", {}))
        outputs["recovery"] = self.recovery_agent.create_plan(state["profile"])
        return {**state, "outputs": outputs}

    def _safety_node(self, state: PlannerState) -> PlannerState:
        review = self.safety_agent.review(state["profile"], state["outputs"])
        return {**state, "review": review}

    def _final_node(self, state: PlannerState) -> PlannerState:
        final_plan = self._format_final_plan(state["profile"], state["outputs"], state["review"])
        return {**state, "final_plan": final_plan}

    def _build_graph(self):
        if StateGraph is None or END is None:
            return None
        graph = StateGraph(PlannerState)
        graph.add_node("profile_analysis", self._profile_node)
        graph.add_node("nutrition_planning", self._nutrition_node)
        graph.add_node("meal_planning", self._meal_planning_node)
        graph.add_node("workout_programming", self._workout_node)
        graph.add_node("recovery_habits", self._recovery_node)
        graph.add_node("safety_review", self._safety_node)
        graph.add_node("final_plan", self._final_node)
        graph.set_entry_point("profile_analysis")
        graph.add_edge("profile_analysis", "nutrition_planning")
        graph.add_edge("nutrition_planning", "meal_planning")
        graph.add_edge("meal_planning", "workout_programming")
        graph.add_edge("workout_programming", "recovery_habits")
        graph.add_edge("recovery_habits", "safety_review")
        graph.add_edge("safety_review", "final_plan")
        graph.add_edge("final_plan", END)
        return graph.compile()

    def generate_plan(self, profile: UserProfile) -> str:
        """Run the multi-agent workflow and return an integrated Markdown plan."""
        compiled_graph = self._build_graph()
        initial_state: PlannerState = {"profile": profile, "outputs": {}}
        if compiled_graph is not None:
            result = compiled_graph.invoke(initial_state)
            return result["final_plan"]

        # Fallback keeps local demo checks smooth if LangGraph has not been installed yet.
        outputs = {
            "profile": self.profile_agent.analyze(profile),
            "nutrition": self.nutrition_agent.create_plan(profile),
            "meal_planning": self.meal_planner_agent.create_plan(profile),
            "workout": self.workout_agent.create_plan(profile),
            "recovery": self.recovery_agent.create_plan(profile),
        }
        review = self.safety_agent.review(profile, outputs)
        return self._format_final_plan(profile, outputs, review)

    def answer_question(self, question: str, existing_plan: str) -> str:
        """Answer follow-up questions using the generated plan as context."""
        return self.qa_agent.answer(question, existing_plan)

    def _format_final_plan(self, profile: UserProfile, outputs: Dict[str, AgentResult], review: AgentResult) -> str:
        bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
        water = estimate_daily_water_liters(profile.weight_kg, profile.activity_level)
        flags = build_safety_flags(profile)
        safety_flags = ", ".join(flags) if flags else "No major self-reported flags detected."
        return format_plan(
            "Health and Fitness Planner Agent",
            {
                "LangGraph Multi-Agent Architecture": (
                    "User Profile → HealthFitnessOrchestrator → ProfileAnalysisAgent → NutritionPlanningAgent → "
                    "MealPlannerAgent → WorkoutProgrammingAgent → RecoveryHabitAgent → SafetyReviewAgent → Final Plan"
                ),
                "Profile Summary": (
                    f"Provider: **{self.provider}** | Model: **{self.effective_model_id}**\n\n"
                    f"BMI estimate: **{bmi}**\n\n"
                    f"Daily hydration estimate: **{water} L**\n\n"
                    f"Safety flags: **{safety_flags}**\n\n"
                    f"{profile.to_prompt()}"
                ),
                outputs["profile"].agent_name: outputs["profile"].content,
                outputs["nutrition"].agent_name: outputs["nutrition"].content,
                outputs["meal_planning"].agent_name: outputs["meal_planning"].content,
                outputs["workout"].agent_name: outputs["workout"].content,
                outputs["recovery"].agent_name: outputs["recovery"].content,
                review.agent_name: review.content,
                "Safety Notice": safety_notice(),
            },
        )
