# Health and Fitness Planner Agent

A professional, production-ready multi-agent health and fitness planning project. The system uses separate specialist Python files for each agent, a LangGraph-based orchestrator, shared tools, a CLI entry point, and a Streamlit app entry point.

> This project provides general wellness guidance only. It is not medical advice.

## Architecture

```text
User Profile
   ↓
main.py / app.py
   ↓
agents/orchestrator.py  LangGraph workflow
   ↓
agents/profile_agent.py
   ↓
agents/nutrition_agent.py
   ↓
agents/meal_planner_agent.py
   ↓
agents/workout_agent.py
   ↓
agents/recovery_agent.py
   ↓
agents/safety_agent.py
   ↓
Final Integrated Health and Fitness Plan
```

## Agent Files

- `agents/profile_agent.py` analyzes goals, constraints, lifestyle, safety priorities, and planning context.
- `agents/nutrition_agent.py` creates general nutrition, hydration, meal-structure, portion, and adherence guidance.
- `agents/meal_planner_agent.py` creates recipe-inspired weekly meal templates, shopping lists, estimated food cost, and simple meal-planning notes.
- `agents/workout_agent.py` creates training structure, warm-up, strength, cardio, mobility, cool-down, progression, and modifications.
- `agents/recovery_agent.py` creates recovery, sleep, hydration, stress, tracking, and habit guidance.
- `agents/safety_agent.py` reviews the full output, flags risks, removes contradictions, and produces the final checklist.
- `agents/qa_agent.py` answers follow-up questions using the generated plan as context.
- `agents/base.py` handles shared OpenAI, Google Gemini, and deterministic demo provider logic.
- `agents/orchestrator.py` combines the agents through a LangGraph workflow.

## Project Structure

```text
Health and Fitness Planner Agent/
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── orchestrator.py
│   ├── profile_agent.py
│   ├── nutrition_agent.py
│   ├── meal_planner_agent.py
│   ├── workout_agent.py
│   ├── recovery_agent.py
│   ├── safety_agent.py
│   └── qa_agent.py
├── tools/
│   ├── __init__.py
│   ├── profile_tools.py
│   ├── metrics_tools.py
│   ├── meal_tools.py
│   ├── safety_tools.py
│   └── formatting_tools.py
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## Features

- Separate Python file for every specialist agent
- LangGraph orchestration through `StateGraph`
- OpenAI support
- Google Gemini support
- Local deterministic demo mode without API keys
- CLI and Streamlit entry points
- Profile validation
- BMI and hydration estimates
- Nutrition, meal planning, workout, recovery, habit, and safety planning
- Recipe-inspired weekly meal templates with shopping lists and estimated food costs
- Optional Spoonacular recipe search helper through `SPOONACULAR_API_KEY`
- Follow-up Q&A based on the generated plan
- Clean GitHub-ready structure with no `.env`, `.gitignore`, cache, or junk files included

## Requirements

- Python 3.10+
- Optional OpenAI API key for OpenAI generation
- Optional Gemini API key for Google Gemini generation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Set one or both provider keys in your terminal or deployment environment.

```bash
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
SPOONACULAR_API_KEY=optional_recipe_search_key_here
```

If no API key is provided, the project automatically runs in deterministic demo mode.

## Run CLI Entry Point

```bash
python main.py --provider demo
```

OpenAI example:

```bash
python main.py --provider openai --model gpt-4.1-mini --goal "Gain Muscle"
```

Gemini example:

```bash
python main.py --provider gemini --model gemini-2.0-flash --goal "Lose Weight"
```

## Run Streamlit Entry Point

```bash
streamlit run app.py
```

## Why This Belongs Under Multi-Agent Systems

This project is not a single-prompt app. It has separate role-based agents, a LangGraph orchestration layer, shared tools, provider routing, validation, safety review, CLI execution, and a Streamlit application interface.

## Validation Checklist

Run these before GitHub upload:

```bash
python -m py_compile main.py app.py agents/*.py tools/*.py
python main.py --provider demo
```

Expected result: no syntax errors and a complete Markdown health and fitness plan printed in the terminal.

## Safety Notes

Generated plans are educational and should not replace professional medical, nutrition, physiotherapy, or coaching advice. Users with injuries, medical conditions, pregnancy-related concerns, chronic pain, eating-disorder history, or medication changes should consult a qualified professional before following a new plan.


## Updated Modular Tool Structure

The original single `tools.py` file has been replaced with a clean `tools/` package:

```text
tools/
├── __init__.py
├── profile_tools.py
├── metrics_tools.py
├── safety_tools.py
└── formatting_tools.py
```

Imports remain stable through `tools/__init__.py`, while each tool category now has its own maintainable Python file.

## Meal Planning Add-On Integration

This version integrates the useful meal-planning logic from the uploaded AI Recipe Meal Planning Agent into the Health and Fitness Planner architecture. Health Fitness remains the main project. The recipe project is not copied as a separate app. Instead, the reusable meal tools are added as `tools/meal_tools.py`, and the new specialist agent is added as `agents/meal_planner_agent.py`.

The integration avoids adding Agno or DuckDuckGo dependencies because the main Health Fitness project already has its own agent base, provider routing, LangGraph workflow, CLI, and Streamlit app. This keeps the project clean, lighter, and easier to run.

New capability added:

- Weekly meal template generation
- Dietary preference filtering
- Estimated calories and protein per day
- Estimated food cost
- Shopping list generation
- Meal-plan insights
- Optional Spoonacular recipe search helper when `SPOONACULAR_API_KEY` is configured

Updated workflow:

```text
ProfileAnalysisAgent
↓
NutritionPlanningAgent
↓
MealPlannerAgent
↓
WorkoutProgrammingAgent
↓
RecoveryHabitAgent
↓
SafetyReviewAgent
↓
Final Plan
```
