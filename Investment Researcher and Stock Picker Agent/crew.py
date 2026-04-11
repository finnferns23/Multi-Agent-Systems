from __future__ import annotations

from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.memory import EntityMemory, LongTermMemory, ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field

from investment_research_and_stock_picker_agent.tools import PushNotificationTool


class TrendingCompany(BaseModel):
    """A company that is currently trending in the news."""

    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason the company is trending")


class TrendingCompanyList(BaseModel):
    """List of trending companies."""

    companies: List[TrendingCompany] = Field(description="List of trending companies")


class CompanyResearch(BaseModel):
    """Detailed research record for a company."""

    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    recent_news: str = Field(description="Recent relevant developments or news")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    risks: str = Field(description="Key risks and challenges")
    investment_potential: str = Field(description="Investment potential and suitability for further consideration")


class CompanyResearchList(BaseModel):
    """Research list for all shortlisted companies."""

    research_list: List[CompanyResearch] = Field(description="Detailed research for all shortlisted companies")


@CrewBase
class InvestmentResearchAndStockPickerAgent:
    """Unified CrewAI project for company discovery, research, analysis, and stock selection."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config["trending_company_finder"],
            tools=[SerperDevTool()],
            memory=True,
            verbose=True,
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SerperDevTool()],
            verbose=True,
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],
            verbose=True,
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_picker"],
            tools=[PushNotificationTool()],
            memory=True,
            verbose=True,
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies"],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_companies(self) -> Task:
        return Task(
            config=self.tasks_config["research_companies"],
            output_pydantic=CompanyResearchList,
        )

    @task
    def analyze_companies(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_companies"],
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company"],
        )

    @crew
    def crew(self) -> Crew:
        manager = Agent(
            config=self.agents_config["manager"],
            allow_delegation=True,
            verbose=True,
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
            memory=True,
            long_term_memory=LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            short_term_memory=ShortTermMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {"model": "text-embedding-3-small"},
                    },
                    type="short_term",
                    path="./memory/",
                )
            ),
            entity_memory=EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {"model": "text-embedding-3-small"},
                    },
                    type="short_term",
                    path="./memory/",
                )
            ),
        )
