# Investment Research and Stock Picker Agent

A production-style CrewAI project that combines:

- trending company discovery from recent news
- structured company research
- comparative analysis and report writing
- final stock selection
- optional push notifications
- memory across runs

This repository is designed to be clean enough for GitHub and practical enough to run locally on Windows.

## What this project does

The workflow is:

1. Find 2-3 trending public companies in a sector
2. Research each company using web search
3. Compare them in a structured analysis report
4. Pick the strongest candidate for further investment consideration
5. Optionally send a push notification with the final decision

## Project structure

```text
Investment_Research_and_Stock_Picker_Agent/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
├── output/
├── memory/
└── src/
    └── investment_research_and_stock_picker_agent/
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── config/
        │   ├── agents.yaml
        │   └── tasks.yaml
        └── tools/
            ├── __init__.py
            └── push_tool.py
```

## Windows setup

### 1) Create and activate a virtual environment

In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

In Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

## 2) Install dependencies

```cmd
pip install -r requirements.txt
```

## 3) Create your environment file

Copy `.env.example` to `.env` and add your keys.

Required:

- `OPENAI_API_KEY`
- `SERPER_API_KEY`

Optional for push notifications:

- `PUSHOVER_USER`
- `PUSHOVER_TOKEN`

## 4) Run the project on Windows

This repo is set up so it runs directly from the project root without package installation.

```cmd
python src\investment_research_and_stock_picker_agent\main.py
```

That is the safest Windows-friendly command for this project.

## Optional: run with CrewAI CLI

If you want to use CrewAI CLI instead, install CrewAI properly and adapt the package layout to your preferred template. For GitHub portfolio use, the direct Python entrypoint is simpler and more reliable.

## Expected outputs

After running, files are written into `output/`:

- `trending_companies.json`
- `research_report.json`
- `final_report.md`
- `decision.md`

Memory artifacts are stored in `memory/`.

## Notes for GitHub

This project is suitable as a portfolio project because it demonstrates:

- multi-agent orchestration
- hierarchical task delegation
- structured Pydantic outputs
- external tool integration
- optional notification workflow
- persistent memory setup
- clean repo organization

## Recommended GitHub repo name

```text
Investment-Research-and-Stock-Picker-Agent
```

## Example `.env`

```env
OPENAI_API_KEY=your_openai_key_here
SERPER_API_KEY=your_serper_key_here
PUSHOVER_USER=your_pushover_user_here
PUSHOVER_TOKEN=your_pushover_token_here
```
