from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.base import Agent


@dataclass
class AgentRegistry:
    _agents: dict[str, Agent] = field(default_factory=dict)

    def register(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    def register_all(self) -> None:
        from app.agents.academic_advisor.agent import AcademicAdvisorAgent
        from app.agents.admin_assistant.agent import AdminAssistantAgent
        from app.agents.admissions.agent import AdmissionsAgent
        from app.agents.campus_navigation.agent import CampusNavigationAgent
        from app.agents.career.agent import CareerAgent
        from app.agents.executive_intelligence.agent import ExecutiveIntelligenceAgent
        from app.agents.faculty_intelligence.agent import FacultyIntelligenceAgent
        from app.agents.knowledge.agent import KnowledgeAgent
        from app.agents.research_assistant.agent import ResearchAssistantAgent
        from app.agents.retention.agent import RetentionAgent
        from app.agents.student_success.agent import StudentSuccessAgent
        from app.agents.timetable.agent import TimetableAgent

        for agent_cls in [
            KnowledgeAgent,
            StudentSuccessAgent,
            AcademicAdvisorAgent,
            TimetableAgent,
            CampusNavigationAgent,
            CareerAgent,
            AdmissionsAgent,
            AdminAssistantAgent,
            FacultyIntelligenceAgent,
            RetentionAgent,
            ResearchAssistantAgent,
            ExecutiveIntelligenceAgent,
        ]:
            self.register(agent_cls())


agent_registry = AgentRegistry()
