"""Optional Neo4j graph backend — falls back to in-memory adjacency graph."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class Neo4jGraphBackend:
    """Query Neo4j when NEO4J_URI is configured."""

    def __init__(self) -> None:
        self._auth = (settings.neo4j_user, settings.neo4j_password)
        self._query_url = f"{settings.neo4j_uri.rstrip('/')}/db/neo4j/tx/commit"

    async def get_neighbors(
        self,
        entity_type: str,
        entity_id: str,
        relationship: str,
    ) -> list[dict[str, Any]]:
        cypher = (
            f"MATCH (a:{entity_type} {{id: $entity_id}})-[r:{relationship}]->(b) "
            "RETURN b.id AS id, labels(b)[0] AS type, b.name AS name LIMIT 25"
        )
        return await self._run(cypher, {"entity_id": entity_id})

    async def list_by_relationship(self, entity_type: str, relationship: str) -> list[dict[str, Any]]:
        cypher = (
            f"MATCH (a:{entity_type})-[r:{relationship}]->(b) "
            "RETURN DISTINCT b.id AS id, labels(b)[0] AS type, b.name AS name LIMIT 50"
        )
        return await self._run(cypher, {})

    async def _run(self, statement: str, parameters: dict[str, Any]) -> list[dict[str, Any]]:
        payload = {"statements": [{"statement": statement, "parameters": parameters}]}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self._query_url, json=payload, auth=self._auth)
                response.raise_for_status()
                data = response.json()
            rows: list[dict[str, Any]] = []
            for result in data.get("results", []):
                columns = result.get("columns", [])
                for row in result.get("data", []):
                    values = row.get("row", [])
                    rows.append(dict(zip(columns, values)))
            return rows
        except Exception as exc:
            logger.warning("neo4j_query_failed error=%s", exc)
            return []


neo4j_backend: Neo4jGraphBackend | None = None


def get_neo4j_backend() -> Neo4jGraphBackend | None:
    global neo4j_backend
    if not settings.neo4j_configured:
        return None
    if neo4j_backend is None:
        neo4j_backend = Neo4jGraphBackend()
    return neo4j_backend
