"""Neo4j Knowledge Graph interface.

Stores entity relationships for multi-hop reasoning:
Company -> Sector, Company -> Peers, Macro -> Sector impact chains, etc.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Entity types
ENTITY_TYPES = [
    "Company", "Sector", "Industry", "Executive",
    "MacroIndicator", "GeopoliticalEvent", "Commodity",
    "Country", "FinancialInstrument",
]

# Relationship types
RELATIONSHIP_TYPES = [
    "BELONGS_TO", "COMPETES_WITH", "SUPPLIES_TO",
    "IMPACTS", "LEADS", "OWNS_STAKE_IN",
    "PRODUCES", "EXPOSED_TO", "TRIGGERS",
    "TRADED_IN", "TRACKS",
]


class KnowledgeGraph:
    """Neo4j-backed knowledge graph for entity relationship queries.

    Supports multi-hop traversal for questions like:
    - "Which companies are exposed to Taiwan supply chain risk?"
    - "What sectors are impacted by rising oil prices?"
    """

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "") -> None:
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None

    def _get_driver(self) -> Any:
        """Lazy-initialize Neo4j driver."""
        if self._driver is None:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self._driver

    def _run_query(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results."""
        driver = self._get_driver()
        with driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    # --- Entity Operations ---

    def merge_entity(self, entity_type: str, properties: dict[str, Any]) -> None:
        """Create or update an entity using MERGE (deduplication)."""
        if entity_type not in ENTITY_TYPES:
            raise ValueError(f"Invalid entity type: {entity_type}. Must be one of {ENTITY_TYPES}")
        key_prop = "ticker" if entity_type == "Company" else "name"
        key_val = properties.get(key_prop, properties.get("name", ""))
        set_clause = ", ".join(f"e.{k} = ${k}" for k in properties if k != key_prop)
        cypher = f"""
            MERGE (e:{entity_type} {{{key_prop}: $key_val}})
            {'SET ' + set_clause if set_clause else ''}
        """
        params = {"key_val": key_val, **properties}
        self._run_query(cypher, params)

    def create_relationship(
        self,
        from_type: str, from_key: str,
        rel_type: str,
        to_type: str, to_key: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Create a relationship between two entities."""
        if from_type not in ENTITY_TYPES:
            raise ValueError(f"Invalid entity type: {from_type}. Must be one of {ENTITY_TYPES}")
        if to_type not in ENTITY_TYPES:
            raise ValueError(f"Invalid entity type: {to_type}. Must be one of {ENTITY_TYPES}")
        if rel_type not in RELATIONSHIP_TYPES:
            raise ValueError(f"Invalid relationship type: {rel_type}. Must be one of {RELATIONSHIP_TYPES}")
        props = properties or {}
        props_str = ""
        if props:
            props_str = " {" + ", ".join(f"{k}: ${k}" for k in props) + "}"
        from_key_prop = "ticker" if from_type == "Company" else "name"
        to_key_prop = "ticker" if to_type == "Company" else "name"
        cypher = f"""
            MATCH (a:{from_type} {{{from_key_prop}: $from_key}})
            MATCH (b:{to_type} {{{to_key_prop}: $to_key}})
            MERGE (a)-[r:{rel_type}{props_str}]->(b)
        """
        params = {"from_key": from_key, "to_key": to_key, **props}
        self._run_query(cypher, params)

    # --- Query Operations ---

    def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a raw Cypher query."""
        return self._run_query(cypher, params)

    def get_company_relationships(self, ticker: str) -> dict[str, Any]:
        """Get all relationships for a company."""
        cypher = """
            MATCH (c:Company {ticker: $ticker})-[r]-(related)
            RETURN type(r) AS relationship, labels(related) AS related_type,
                   related.name AS related_name, related.ticker AS related_ticker,
                   properties(r) AS rel_properties
        """
        results = self._run_query(cypher, {"ticker": ticker})
        return {"ticker": ticker, "relationships": results}

    def find_supply_chain(self, ticker: str, depth: int = 3) -> list[dict[str, Any]]:
        """Trace supply chain relationships up to N hops."""
        cypher = f"""
            MATCH path = (c:Company {{ticker: $ticker}})-[:SUPPLIES_TO*1..{depth}]-(related:Company)
            RETURN [n IN nodes(path) | n.ticker] AS chain,
                   length(path) AS depth
            ORDER BY depth
        """
        return self._run_query(cypher, {"ticker": ticker})

    def find_sector_exposure(self, indicator: str) -> list[dict[str, Any]]:
        """Find which sectors are impacted by a macro indicator."""
        cypher = """
            MATCH (m:MacroIndicator {name: $indicator})-[r:IMPACTS]->(s:Sector)
            RETURN s.name AS sector, r.direction AS direction, r.lag_months AS lag
            ORDER BY r.direction
        """
        return self._run_query(cypher, {"indicator": indicator})

    def find_exposed_companies(self, commodity: str, min_exposure: float = 0.05) -> list[dict[str, Any]]:
        """Find companies exposed to a commodity."""
        cypher = """
            MATCH (c:Company)-[r:EXPOSED_TO]->(cm:Commodity {name: $commodity})
            WHERE r.cost_pct_revenue >= $min_exposure
            RETURN c.ticker AS ticker, c.name AS name, r.cost_pct_revenue AS exposure
            ORDER BY r.cost_pct_revenue DESC
        """
        return self._run_query(cypher, {"commodity": commodity, "min_exposure": min_exposure})

    def close(self) -> None:
        """Close the Neo4j driver."""
        if self._driver:
            self._driver.close()
            self._driver = None
