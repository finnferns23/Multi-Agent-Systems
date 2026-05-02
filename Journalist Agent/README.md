# AI Journalist Agent

AI Journalist Agent is a clean Streamlit and command line project that researches a topic, gathers relevant online sources, drafts an article, and performs editorial refinement through a coordinated multi agent workflow.

## Recommended repository placement

Place this project in:

```text
Multi Agent Systems/AI Journalist Agent
```

This is the best fit because the workflow uses three cooperating agents: Searcher, Writer, and Editor. It is more than a simple AI app and it is not just a single agent system.

## Project structure

```text
AI Journalist Agent/
├── agents/
│   ├── __init__.py
│   ├── editor_agent.py
│   ├── searcher_agent.py
│   └── writer_agent.py
├── tools/
│   ├── __init__.py
│   ├── newspaper_tool.py
│   └── serpapi_tool.py
├── workflows/
│   ├── __init__.py
│   └── journalist_workflow.py
├── app.py
├── config.py
├── main.py
├── README.md
└── requirements.txt
```

## What each part does

| File or folder | Purpose |
| --- | --- |
| `agents/searcher_agent.py` | Builds the research agent that finds credible article source URLs. |
| `agents/writer_agent.py` | Builds the writing agent that reads sources and drafts the article. |
| `agents/editor_agent.py` | Builds the editor agent that coordinates the team and performs final review. |
| `tools/serpapi_tool.py` | Creates the SerpAPI search tool. |
| `tools/newspaper_tool.py` | Creates the Newspaper4k article extraction tool. |
| `workflows/journalist_workflow.py` | Runs the complete article generation workflow. |
| `main.py` | Command line entry point. |
| `app.py` | Streamlit web app entry point. |
| `config.py` | Validates API keys, model, and article length settings. |
| `requirements.txt` | Lists the required packages. |

## Setup

Create and activate a virtual environment first.

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Set environment variables for CLI use.

```bash
set OPENAI_API_KEY=your_openai_api_key
set SERPAPI_API_KEY=your_serpapi_api_key
```

For PowerShell, use:

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:SERPAPI_API_KEY="your_serpapi_api_key"
```

## Run the Streamlit app

```bash
streamlit run app.py
```

Enter your OpenAI and SerpAPI keys in the sidebar, then provide an article topic.

## Run from command line

```bash
python main.py "The future of AI agents in business operations" --length balanced
```

Length options are:

```text
short
balanced
long
```

## Notes

LangGraph and LangChain were considered, but this project does not need an extra graph layer because Agno already handles the agent team orchestration cleanly. Keeping the stack focused makes the project easier to run, easier to explain on GitHub, and less likely to break from unnecessary dependencies.

## Validation completed

The updated project was checked for:

```text
Python syntax compilation
Clean imports at the top of files
Separate agent modules
Separate tool modules
Streamlit entry point
Command line entry point
Updated requirements
Clean GitHub ready folder structure
```
