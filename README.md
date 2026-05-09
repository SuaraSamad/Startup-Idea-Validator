---
title: Startup Idea Validator
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
---
# Startup Idea Validator

A multi-agent AI app built with CrewAI, OpenAI, and Gradio to validate startup ideas with:

- Market research
- Competitor analysis
- Final GO/NO-GO validation report

## Tech Stack

- CrewAI
- crewai-tools (`SerperDevTool`, `ScrapeWebsiteTool`)
- OpenAI (`gpt-4o-mini`)
- Gradio
- python-dotenv

## Project Structure

```
startup-validator/
├── app.py
├── crew.py
├── tools.py
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
├── pyproject.toml
├── uv.lock
├── .env.example
├── requirements.txt
└── README.md
```

## 1) Clone the Repository

```bash
git clone <your-repo-url>
cd startup-validator
```

## 2) Create and Configure Environment Variables

Create a local `.env` file:

```bash
cp .env.example .env
```

Then set:

```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

Get your keys from:

- [OpenAI Platform](https://platform.openai.com/)
- [Serper](https://serper.dev/)

## 3) Install Dependencies

```bash
uv sync
```

## 4) Run Locally

```bash
uv run python app.py
```

The app will run on `0.0.0.0:7860`.

## 5) Deploy to Hugging Face Spaces

1. Create a new Space on Hugging Face (SDK: **Gradio**).
2. Push this project to a GitHub repository.
3. Connect the GitHub repo to your Hugging Face Space.
4. In Space settings, add secrets:
   - `OPENAI_API_KEY`
   - `SERPER_API_KEY`
5. Ensure `pyproject.toml`, `uv.lock`, and `app.py` are in the repo root.
6. Redeploy the Space; Hugging Face will install dependencies and launch the app.

### Optional: export `requirements.txt` from `uv.lock`

If your deployment target requires `requirements.txt`, generate it from the lockfile:

```bash
uv export --format requirements-txt --no-hashes -o requirements.txt
```

## Notes

- API keys are never hardcoded in the source code.
- Agent and task behavior is configured via YAML files in `config/`.
- If agent execution fails, the UI returns a readable error instead of a blank output.
