"""Tool initialization for CrewAI agents."""

import os

from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv


def get_research_tools():
    """Create shared research tools used by market and competitor agents."""
    load_dotenv()

    if not os.getenv("SERPER_API_KEY"):
        raise ValueError(
            "SERPER_API_KEY is missing. Add it to your .env file before running."
        )

    return [SerperDevTool(), ScrapeWebsiteTool()]
