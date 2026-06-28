from fastapi.testclient import TestClient
import pytest

from evidra.api import create_app
from evidra.memory import crystallize_experience, link_memories, memory_graph_summary, recall_experience


def test_crystallize_and_recall_experience(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'memory.db'}")
    with TestClient(app) as client:
        # 1. Crystallize experience via API
        res = client.post(
            "/api/memory/crystallize",
            json={
                "concept": "paid leave policy",
                "procedure": "Employees receive 24 days each year, submitted 5 days in advance.",
                "domain": "hr",
                "confidence": 0.95,
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["concept"] == "paid leave policy"
        assert data["executions"] == 1

        # 2. Reinforce memory on repeat crystallization
        res2 = client.post(
            "/api/memory/crystallize",
            json={
                "concept": "paid leave policy",
                "procedure": "Employees receive 24 days each year, submitted 5 days in advance.",
                "domain": "hr",
            },
        )
        assert res2.status_code == 201
        assert res2.json()["executions"] == 2

        # 3. Recall memory via query
        recall_res = client.get("/api/memory/recall?q=leave+days")
        assert recall_res.status_code == 200
        recalled = recall_res.json()
        assert len(recalled) == 1
        assert recalled[0]["concept"] == "paid leave policy"
        assert "24 days" in recalled[0]["procedure"]

        # 4. Inspect knowledge graph summary
        graph_res = client.get("/api/memory/graph")
        assert graph_res.status_code == 200
        graph = graph_res.json()
        assert graph["node_count"] == 1
        assert "hr" in graph["domains"]
        assert graph["total_reinforced_executions"] >= 2
