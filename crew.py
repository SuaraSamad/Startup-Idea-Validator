"""Crew definition for startup idea validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from dotenv import load_dotenv

from tools import get_research_tools


BASE_DIR = Path(__file__).resolve().parent


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load yaml content into a dictionary."""
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _build_llm() -> LLM:
    """Create the OpenAI-backed LLM used by all agents."""
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file before running.")

    return LLM(
        model="openai/gpt-4o-mini",
        api_key=openai_key,
    )


def run_crew(idea: str) -> dict[str, str]:
    """Run the startup validation crew and return parsed outputs for the UI."""
    if not idea.strip():
        raise ValueError("Startup idea cannot be empty.")

    agents_config = _load_yaml(BASE_DIR / "config" / "agents.yaml")
    tasks_config = _load_yaml(BASE_DIR / "config" / "tasks.yaml")

    llm = _build_llm()
    research_tools = get_research_tools()

    # Agent 1: market research.
    market_researcher = Agent(
        role=agents_config["market_researcher"]["role"],
        goal=agents_config["market_researcher"]["goal"],
        backstory=agents_config["market_researcher"]["backstory"],
        tools=research_tools,
        llm=llm,
        verbose=True,
    )

    # Agent 2: competitor analysis.
    competitor_analyst = Agent(
        role=agents_config["competitor_analyst"]["role"],
        goal=agents_config["competitor_analyst"]["goal"],
        backstory=agents_config["competitor_analyst"]["backstory"],
        tools=research_tools,
        llm=llm,
        verbose=True,
    )

    # Agent 3: final startup validation.
    startup_validator = Agent(
        role=agents_config["startup_validator"]["role"],
        goal=agents_config["startup_validator"]["goal"],
        backstory=agents_config["startup_validator"]["backstory"],
        llm=llm,
        verbose=True,
    )

    market_task = Task(
        description=tasks_config["market_research_task"]["description"].format(idea=idea),
        expected_output=tasks_config["market_research_task"]["expected_output"],
        agent=market_researcher,
    )
    competitor_task = Task(
        description=tasks_config["competitor_analysis_task"]["description"].format(idea=idea),
        expected_output=tasks_config["competitor_analysis_task"]["expected_output"],
        agent=competitor_analyst,
    )
    validation_task = Task(
        description=tasks_config["validation_task"]["description"].format(idea=idea),
        expected_output=tasks_config["validation_task"]["expected_output"],
        agent=startup_validator,
    )

    crew = Crew(
        agents=[market_researcher, competitor_analyst, startup_validator],
        tasks=[market_task, competitor_task, validation_task],
        process=Process.sequential,
        memory=False,
        verbose=True,
    )

    crew_output = crew.kickoff(inputs={"idea": idea})

    market_output = "No output generated."
    competitor_output = "No output generated."
    validation_output = "No output generated."

    def _task_output_text(task_output: Any) -> str:
        """Extract plain text from CrewAI task output objects safely."""
        for attr in ("raw", "output", "result"):
            value = getattr(task_output, attr, None)
            if value:
                return str(value)
        return str(task_output)

    # CrewAI commonly returns task outputs in order; we map them to tabs safely.
    task_outputs = getattr(crew_output, "tasks_output", None) or []
    if len(task_outputs) >= 3:
        market_output = _task_output_text(task_outputs[0])
        competitor_output = _task_output_text(task_outputs[1])
        validation_output = _task_output_text(task_outputs[2])

    raw_output = str(crew_output)

    return {
        "market_output": market_output,
        "competitor_output": competitor_output,
        "validation_output": validation_output,
        "raw_output": raw_output,
    }
