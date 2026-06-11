from app.agents.base import Agent, AgentContext, AgentResult
from app.services.knowledge_graph import knowledge_graph_service


class CampusNavigationAgent(Agent):
    name = "campus_navigation"
    description = "Building directions, room locations, walking time estimates"
    keywords = [
        "where is", "building", "room", "directions", "walk", "campus", "library",
        "engineering", "location", "how long",
    ]

    def can_handle(self, message: str, user_role: str) -> float:
        return self._keyword_score(message)

    async def run(self, context: AgentContext) -> AgentResult:
        lower = context.message.lower()
        building = await knowledge_graph_service.find_building(context.message)

        if building:
            room_info = ""
            if "matched_room" in building:
                room_info = f" Room {building['matched_room']} ({building['room_label']})."
            msg = f"{building['name']} ({building['code']}) is on campus.{room_info}"
        else:
            msg = (
                "Campus buildings: Engineering Hall (ENG), Central Library (LIB), "
                "Business School (BUS), Student Center (STC). "
                "Specify a building or room number for directions."
            )

        if "how long" in lower or "walk" in lower:
            from_b = "library" if "library" in lower else None
            to_b = "eng-hall" if "engineering" in lower else "business-school" if "business" in lower else None
            if from_b and to_b:
                minutes = await knowledge_graph_service.walking_time(from_b, to_b)
                if minutes:
                    msg += f" Walking time: approximately {minutes} minutes."

        return AgentResult(
            agent=self.name,
            message=msg,
            metadata={"building": building},
        )
