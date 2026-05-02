# Travel Agent — Multi-Agent AI Travel Planning System

## Overview

This application functions as both a **travel agent** and an **AI travel planner**, using a coordinated multi-agent workflow to generate structured, realistic travel itineraries.

Instead of relying on one single model response, the system separates the planning process into specialist agents, gathers tool-assisted context where available, and then coordinates everything into a final day-by-day travel plan.

## Why this project is structured this way

The project uses a **minimal production-ready modular structure**. It avoids unnecessary folders while still separating the main responsibilities clearly:

- UI logic stays in `app.py`
- Multi-agent planning logic stays in `agents.py`
- MCP-style tools stay in `tools.py`
- The Streamlit launcher stays in `main.py`

This keeps the project clean, easy to run, easy to review, and suitable for a GitHub **Multi-Agent-Systems** portfolio repository.

## Core Architecture

The system is built around the following specialist agents:

- **MCP Planner Agent**  
  Prepares the planning context, date window, and available MCP-style tools.

- **Destination Research Agent**  
  Looks for destination context such as attractions, food areas, neighborhoods, and seasonal travel notes.

- **Accommodation Agent**  
  Suggests stay-area strategy based on budget, accommodation preference, and travel style.

- **Transport Agent**  
  Handles route estimation and local movement planning when Google Maps is configured.

- **Safety and Budget Agent**  
  Adds safety considerations and broad budget-planning guidance.

- **Accessibility Agent**  
  Adds accessibility-aware guidance when the user provides accessibility or special travel requirements.

- **Itinerary Coordinator Agent**  
  Uses OpenAI or Ollama to combine the specialist research into one final itinerary.

## Features

- Multi-agent travel planning workflow
- MCP-style local tool registry
- OpenAI planner mode
- Ollama local model mode
- Optional SerpAPI live web-search integration
- Optional Google Maps route estimation
- Markdown itinerary export
- `.ics` calendar export
- Specialist-agent research pack view
- Clear verification notes for changeable travel information

## Accuracy and anti-hallucination design

The app is designed to reduce hallucination risk by:

- Separating research from final itinerary writing
- Showing the specialist-agent research pack when requested
- Using live search only when SerpAPI is configured
- Treating prices, opening hours, visa rules, hotel availability, weather, route details, and travel policies as verification items unless confirmed by current sources
- Avoiding fabricated exact prices or booking claims
- Gracefully continuing when optional APIs are missing

## Project Structure

```text
Travel_Agent_Production/
├── app.py              # Streamlit interface and user workflow
├── main.py             # Python launcher for Streamlit
├── agents.py           # Agent classes, model wrappers, orchestration, and calendar export
├── tools.py            # MCP-style tool registry, SerpAPI search, Google Maps route tool
├── requirements.txt    # Runtime dependencies
├── .env.example        # Environment variable template
└── README.md           # Setup, usage, and architecture guide
```

There are no nested source folders. The project remains simple while still keeping agents and tools separate.

## Requirements

- Python 3.10 or newer
- Internet connection for OpenAI, SerpAPI, and Google Maps modes
- Optional: Ollama installed and running for local model mode

## Installation

Create and activate a virtual environment first.

### Windows PowerShell

```powershell
cd Travel_Agent_Production
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
cd Travel_Agent_Production
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Setup

Copy `.env.example` to `.env` and fill in the keys you want to use.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

### OpenAI mode

```text
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

### Optional live tools

```text
SERPAPI_API_KEY=your_serpapi_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### Optional Ollama mode

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

For Ollama mode, install Ollama separately, start it, and pull a model:

```bash
ollama pull llama3.2
```

## How to Run

Recommended:

```bash
python main.py
```

Alternative:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## How to Use

1. Select the planner model provider in the sidebar.
2. Add API keys through `.env` or the sidebar fields.
3. Enter the destination, origin, date, trip length, budget, travelers, pace, accommodation style, preferences, and accessibility needs.
4. Click **Generate Travel Plan**.
5. Review the final itinerary.
6. Download the itinerary as Markdown or as an `.ics` calendar file.
7. Optionally enable **Show specialist-agent research pack** to inspect the agent outputs.

## MCP-Style Tool Layer

The project includes a lightweight local MCP-style tool registry in `tools.py`. It gives the agents a stable tool interface without requiring a separate remote MCP server.

Registered tools:

- `web_search` — searches current travel information through SerpAPI when configured
- `route_distance` — estimates route distance and duration through Google Maps when configured
- `date_window` — creates a structured travel date range

This is not a remote MCP server. It is a local MCP-style architecture designed to keep the project simple, modular, and runnable.

## Dependency Summary

- `streamlit` — web application interface
- `openai` — OpenAI planner mode using the Responses API client
- `requests` — SerpAPI, Google Maps, and Ollama HTTP calls
- `python-dotenv` — environment variable loading from `.env`
- `icalendar` — downloadable `.ics` calendar generation

## Validation

The project is designed to pass Python compilation checks:

```bash
python -m compileall app.py main.py agents.py tools.py
```

This validates Python syntax across the application entry point, agent layer, and tool layer.

## Troubleshooting

### OpenAI mode says the API key is required

Add `OPENAI_API_KEY` in `.env` or paste it into the sidebar field.

### Ollama mode fails

Make sure Ollama is running and the selected model is installed:

```bash
ollama list
ollama pull llama3.2
```

### Live research is empty

Add a valid `SERPAPI_API_KEY`. Without it, the app still runs, but research sections are marked as needing manual verification.

### Route estimates are skipped

Add a valid `GOOGLE_MAPS_API_KEY` and provide both origin and destination.

### Streamlit command is not found

Run the app with:

```bash
python main.py
```

or reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Production Notes

For a deployed client-facing version:

- Store API keys as server-side secrets
- Avoid exposing private keys in the browser UI
- Add authentication if multiple users will access the app
- Add rate limiting for public deployments
- Add logging and error monitoring
- Track model/API usage and cost
- Add stronger validation for destination, date, and budget fields
- Review legal, visa, medical, and travel-risk disclaimers before commercial use

## Recommended GitHub Category

This project fits best under:

```text
Multi-Agent-Systems
```

It can also be cross-referenced as an AI app, but the main architecture is multi-agent orchestration.

## License

Use this project as a portfolio, capstone, or internal prototype. Add your preferred license before public distribution.
