"""Compounding Experiential Memory & Procedural Knowledge Graph.

Inspired by Memorable (https://www.memorable.sh/):
Agents should accumulate verified experience instead of resetting after every turn.
When an oral interrogation completes, verified facts and operational procedures
crystallize into an evolving, durable graph of organizational intelligence.
"""

from datetime import datetime, timezone
import json
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import relationship

from .db import Base


class MemoryNode(Base):
    """A durable unit of accumulated procedural or factual intelligence."""

    __tablename__ = "memory_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    domain = Column(String(128), index=True, default="general")
    concept = Column(String(256), index=True, nullable=False)
    procedure = Column(Text, nullable=False)
    source_digest = Column(String(64), nullable=True)
    confidence = Column(Float, default=1.0)
    execution_count = Column(Integer, default=1)
    verified_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_recalled_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    outgoing_edges = relationship(
        "MemoryEdge",
        foreign_keys="MemoryEdge.source_id",
        cascade="all, delete-orphan",
    )


class MemoryEdge(Base):
    """Relational connection between concepts forming an evolving procedural graph."""

    __tablename__ = "memory_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_id = Column(String(36), ForeignKey("memory_nodes.id"), nullable=False)
    target_id = Column(String(36), ForeignKey("memory_nodes.id"), nullable=False)
    relation = Column(String(64), default="leads_to")  # e.g., leads_to, prerequisite, verifies
    weight = Column(Float, default=1.0)


def crystallize_experience(
    session,
    concept: str,
    procedure: str,
    domain: str = "general",
    source_digest: Optional[str] = None,
    confidence: float = 1.0,
) -> MemoryNode:
    """Commit a verified question/answer procedure to durable organizational memory.
    
    If the procedure already exists for this concept, reinforce its execution count
    and update confidence, mimicking biological neuroplastic reinforcement.
    """
    clean_concept = concept.strip().lower()
    existing = session.scalars(
        select(MemoryNode).where(
            MemoryNode.concept == clean_concept,
            MemoryNode.domain == domain,
        )
    ).first()

    now = datetime.now(timezone.utc)
    if existing:
        existing.execution_count += 1
        existing.last_recalled_at = now
        existing.confidence = min(1.0, existing.confidence + 0.05)
        if len(procedure) > len(existing.procedure):
            existing.procedure = procedure
        session.commit()
        return existing

    node = MemoryNode(
        domain=domain,
        concept=clean_concept,
        procedure=procedure,
        source_digest=source_digest,
        confidence=confidence,
        execution_count=1,
        verified_at=now,
        last_recalled_at=now,
    )
    session.add(node)
    session.commit()
    return node


def recall_experience(
    session,
    query: str,
    domain: Optional[str] = None,
    limit: int = 3,
) -> List[Dict]:
    """Search durable memory for previously verified operational procedures.
    
    Allows the agent to compose past experiences without making redundant LLM calls.
    """
    clean_query = query.strip().lower()
    stmt = select(MemoryNode)
    if domain:
        stmt = stmt.where(MemoryNode.domain == domain)

    all_nodes = session.scalars(stmt).all()
    if not all_nodes:
        return []

    # Score based on lexical and concept overlap reinforced by execution count
    query_tokens = set(clean_query.split())
    scored = []
    for node in all_nodes:
        node_tokens = set(node.concept.split()).union(set(node.procedure.lower().split()[:20]))
        overlap = len(query_tokens.intersection(node_tokens))
        if overlap > 0 or clean_query in node.concept or node.concept in clean_query:
            score = (overlap * 2.0) + (node.execution_count * 0.1) + node.confidence
            scored.append((score, node))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    now = datetime.now(timezone.utc)
    for score, node in scored[:limit]:
        node.last_recalled_at = now
        node.execution_count += 1
        results.append(
            {
                "id": node.id,
                "concept": node.concept,
                "procedure": node.procedure,
                "domain": node.domain,
                "confidence": node.confidence,
                "executions": node.execution_count,
                "relevance_score": score,
            }
        )
    session.commit()
    return results


def link_memories(
    session,
    source_id: str,
    target_id: str,
    relation: str = "leads_to",
    weight: float = 1.0,
) -> MemoryEdge:
    """Connect two verified memories into an evolving procedural knowledge graph."""
    edge = MemoryEdge(
        source_id=source_id,
        target_id=target_id,
        relation=relation,
        weight=weight,
    )
    session.add(edge)
    session.commit()
    return edge


def memory_graph_summary(session) -> Dict:
    """Export the compounding knowledge graph statistics."""
    nodes = session.scalars(select(MemoryNode)).all()
    edges = session.scalars(select(MemoryEdge)).all()
    total_executions = sum(n.execution_count for n in nodes) if nodes else 0
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "total_reinforced_executions": total_executions,
        "domains": sorted(list({n.domain for n in nodes})),
        "nodes": [
            {
                "id": n.id,
                "concept": n.concept,
                "domain": n.domain,
                "procedure": n.procedure[:180] + ("..." if len(n.procedure) > 180 else ""),
                "executions": n.execution_count,
                "confidence": n.confidence,
            }
            for n in nodes[:30]
        ],
        "edges": [
            {
                "id": e.id,
                "source_id": e.source_id,
                "target_id": e.target_id,
                "relation": e.relation,
                "weight": e.weight,
            }
            for e in edges[:50]
        ],
    }
