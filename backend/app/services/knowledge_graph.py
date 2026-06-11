from __future__ import annotations

from typing import Any
from uuid import UUID

from app.services.demo_data import CAMPUS_BUILDINGS
from app.services.graph_sync import graph_sync_service


class KnowledgeGraphService:
    """Postgres/in-memory adjacency graph for cross-entity reasoning."""

    async def get_related(
        self,
        entity_type: str,
        entity_id: str,
        relationship: str,
    ) -> list[dict[str, Any]]:
        return await graph_sync_service.get_neighbors(entity_type, entity_id, relationship)

    async def query(self, pattern: str) -> list[dict[str, Any]]:
        """Simple pattern queries: 'student:* teaches', 'building:eng-hall rooms'."""
        parts = pattern.strip().split()
        if len(parts) < 2:
            return []
        entity_part, rel = parts[0], parts[1]
        if ":" in entity_part:
            etype, eid = entity_part.split(":", 1)
            if eid == "*":
                return await graph_sync_service.list_by_relationship(etype, rel)
            return await self.get_related(etype, eid, rel)
        return []

    async def professors_for_program(self, program: str) -> list[dict[str, Any]]:
        courses = await graph_sync_service.get_neighbors("program", program, "requires_course")
        professors: list[dict[str, Any]] = []
        seen: set[str] = set()
        for course in courses:
            teachers = await graph_sync_service.get_neighbors("course", course["id"], "taught_by")
            for t in teachers:
                if t["id"] not in seen:
                    seen.add(t["id"])
                    professors.append(t)
        return professors

    async def find_building(self, query: str) -> dict[str, Any] | None:
        lower = query.lower()
        for b in CAMPUS_BUILDINGS:
            if b["name"].lower() in lower or b["code"].lower() in lower:
                return b
            for room, label in b.get("rooms", {}).items():
                if room in lower or label.lower() in lower:
                    return {**b, "matched_room": room, "room_label": label}
        return None

    async def walking_time(self, from_id: str, to_id: str) -> int | None:
        from app.services.demo_data import WALKING_TIMES

        return WALKING_TIMES.get((from_id, to_id)) or WALKING_TIMES.get((to_id, from_id))


knowledge_graph_service = KnowledgeGraphService()
