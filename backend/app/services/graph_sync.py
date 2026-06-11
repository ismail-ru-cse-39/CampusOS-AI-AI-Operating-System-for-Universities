from __future__ import annotations

from typing import Any

from app.services.demo_data import CAMPUS_BUILDINGS


class GraphSyncService:
    """Postgres-only graph relations stub — syncs from demo entity data."""

    def __init__(self) -> None:
        self._edges: list[dict[str, str]] = []
        self._entities: dict[str, dict[str, Any]] = {}
        self._bootstrap()

    def _bootstrap(self) -> None:
        self._entities["program:bsc-cs"] = {"id": "bsc-cs", "type": "program", "name": "BSc Computer Science"}
        self._entities["course:CS401"] = {"id": "CS401", "type": "course", "name": "Machine Learning"}
        self._entities["course:CS350"] = {"id": "CS350", "type": "course", "name": "Databases"}
        self._entities["course:MATH301"] = {"id": "MATH301", "type": "course", "name": "Statistics"}
        self._entities["faculty:dr-smith"] = {"id": "dr-smith", "type": "faculty", "name": "Dr. Smith"}
        self._entities["faculty:dr-chen"] = {"id": "dr-chen", "type": "faculty", "name": "Dr. Chen"}
        self._entities["student:alex"] = {"id": "alex", "type": "student", "name": "Alex Johnson"}

        for b in CAMPUS_BUILDINGS:
            self._entities[f"building:{b['id']}"] = {"id": b["id"], "type": "building", "name": b["name"]}

        edges = [
            ("program", "bsc-cs", "requires_course", "course", "CS401"),
            ("program", "bsc-cs", "requires_course", "course", "CS350"),
            ("program", "bsc-cs", "requires_course", "course", "MATH301"),
            ("course", "CS401", "taught_by", "faculty", "dr-smith"),
            ("course", "CS350", "taught_by", "faculty", "dr-chen"),
            ("course", "MATH301", "taught_by", "faculty", "dr-chen"),
            ("student", "alex", "enrolled_in", "course", "CS401"),
            ("student", "alex", "enrolled_in", "course", "CS350"),
            ("course", "CS401", "located_in", "building", "eng-hall"),
            ("building", "eng-hall", "connected_to", "building", "library"),
            ("building", "library", "connected_to", "building", "business-school"),
        ]
        for src_type, src_id, rel, tgt_type, tgt_id in edges:
            self._edges.append(
                {
                    "source_type": src_type,
                    "source_id": src_id,
                    "relationship": rel,
                    "target_type": tgt_type,
                    "target_id": tgt_id,
                }
            )

    async def sync_from_postgres(self) -> dict[str, int]:
        """Stub — would pull users, courses, enrollments from DB."""
        return {
            "entities": len(self._entities),
            "edges": len(self._edges),
            "status": "demo_sync_complete",
        }

    async def get_neighbors(
        self,
        entity_type: str,
        entity_id: str,
        relationship: str,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for edge in self._edges:
            if (
                edge["source_type"] == entity_type
                and edge["source_id"] == entity_id
                and edge["relationship"] == relationship
            ):
                key = f"{edge['target_type']}:{edge['target_id']}"
                entity = self._entities.get(key)
                if entity:
                    results.append(entity)
        return results

    async def list_by_relationship(self, entity_type: str, relationship: str) -> list[dict[str, Any]]:
        seen: set[str] = set()
        results: list[dict[str, Any]] = []
        for edge in self._edges:
            if edge["source_type"] == entity_type and edge["relationship"] == relationship:
                key = f"{edge['target_type']}:{edge['target_id']}"
                if key not in seen:
                    seen.add(key)
                    entity = self._entities.get(key)
                    if entity:
                        results.append(entity)
        return results


graph_sync_service = GraphSyncService()
