"""Unit tests for the 4 unified capabilities in VoxDoc:
1. Wispr Flow: Verbal speech polish
2. Proto: Adversarial document sparring
3. Memorable: Compounding procedural memory graph & auto-crystallization
4. RightNow AI: Low-latency TTFT tracking
"""

from fastapi.testclient import TestClient
import pytest

from evidra.api import create_app
from evidra.db import Passage
from evidra.memory import memory_graph_summary, recall_experience
from evidra.pipeline import execute
from evidra.voice import polish_spoken_text


def test_wispr_flow_verbal_polish():
    # Eliminates filler words, capitalizes, trims spaces
    raw = "um so basically like we have 24 days of paid leave uh right"
    polished = polish_spoken_text(raw)
    assert "um" not in polished.lower()
    assert "basically" not in polished.lower()
    assert "24 days of paid leave" in polished
    assert polished.startswith("We have") or polished.startswith("Right") or "24 days" in polished


def test_proto_adversarial_sparring():
    passages = [
        Passage(
            id="1",
            document_id="doc-1",
            locator="Section 1",
            text="Employees receive 24 days of paid leave each year, requested 5 days in advance.",
        )
    ]
    result = execute("paid leave policy", passages, mode="sparring")
    assert result["disposition"] == "answer"
    assert result["mode"] == "sparring"
    assert "⚔️ [ADVERSARIAL SPARRING AUDIT" in result["answer"]
    assert "Ambiguities" in result["answer"] or "Loopholes" in result["answer"]
    assert result["citations"] == ["1"]


def test_memorable_procedural_mode():
    passages = [
        Passage(
            id="2",
            document_id="doc-2",
            locator="Section 2",
            text="To claim expenses and reimbursement, first submit the reimbursement form. Second, attach original receipts. Third, wait for manager review. Finally, funds are disbursed in 3 business days.",
        )
    ]
    result = execute("How to claim expenses", passages, mode="procedural")
    assert result["disposition"] == "answer"
    assert result["mode"] == "procedural"
    assert "🧠 [COMPOUNDING PROCEDURAL GRAPH" in result["answer"]
    assert "Step 1" in result["answer"]
    assert result["citations"] == ["2"]


def test_api_auto_crystallization_into_memory(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'unified.db'}")
    with TestClient(app) as client:
        # 1. Ask a question on the demo handbook
        demo_res = client.post("/api/demo", json={})
        assert demo_res.status_code == 200
        doc = demo_res.json()

        # 2. Ask question with mode="sparring"
        spar_res = client.post(
            "/api/questions",
            json={
                "document_id": doc["id"],
                "question": "How many days of paid leave do I get?",
                "mode": "sparring",
            },
        )
        assert spar_res.status_code == 201
        spar_data = spar_res.json()
        assert spar_data["mode"] == "sparring"
        assert "⚔️ [ADVERSARIAL SPARRING AUDIT" in spar_data["answer"]

        # 3. Verify it crystallized into Memorable memory graph
        mem_res = client.get("/api/memory/graph")
        assert mem_res.status_code == 200
        graph = mem_res.json()
        assert graph["node_count"] >= 1
        assert any("paid leave" in node["concept"] for node in graph["nodes"])
