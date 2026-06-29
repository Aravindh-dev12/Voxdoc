"""VoxDoc Command Line Interface (CLI).

Install and use VoxDoc directly anywhere:
  voxdoc serve --api-key <RIGHTNOW_OR_OPENAI_KEY>
  voxdoc ask document.pdf "What are the payment terms?" --api-key <KEY>
  voxdoc memory
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="voxdoc",
        description="VoxDoc — The Voice-Native Interrogation Agent & Compounding Memory Runtime.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="VoxDoc 0.1.0 by Aravindhan (https://github.com/Aravindh-dev12/Voxdoc)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Launch the VoxDoc API & web interface server")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    serve_parser.add_argument("--api-key", help="RightNow AI / OpenAI API Key for ultra-fast GPU inference")
    serve_parser.add_argument(
        "--provider",
        choices=["rightnow", "openai", "transformers", "ollama", "extractive"],
        help="Inference provider",
    )
    serve_parser.add_argument("--public", action="store_true", help="Enable public visitor isolation")

    # Command: ask
    ask_parser = subparsers.add_parser("ask", help="Interrogate a document directly from your terminal")
    ask_parser.add_argument("document", help="Path to PDF, Markdown, or text file")
    ask_parser.add_argument("question", help="Question to ask about the document")
    ask_parser.add_argument("--api-key", help="RightNow AI / OpenAI API Key")
    ask_parser.add_argument(
        "--provider",
        choices=["rightnow", "openai", "transformers", "ollama", "extractive"],
        default="extractive",
    )

    # Command: memory
    mem_parser = subparsers.add_parser("memory", help="Inspect organizational compounding memory graph")
    mem_parser.add_argument("--summary", action="store_true", default=True, help="Print memory graph summary")

    args = parser.parse_args()

    if args.command == "serve":
        if args.api_key:
            os.environ["RIGHTNOW_API_KEY"] = args.api_key
        if args.provider:
            os.environ["EVIDRA_PROVIDER"] = args.provider
        if args.public:
            os.environ["EVIDRA_PUBLIC"] = "1"

        print(f"Starting VoxDoc on http://{args.host}:{args.port}")
        import uvicorn
        from .api import create_app

        uvicorn.run(create_app(), host=args.host, port=args.port)

    elif args.command == "ask":
        doc_path = Path(args.document)
        if not doc_path.is_file():
            print(f"Error: Document not found at {doc_path}", file=sys.stderr)
            sys.exit(1)

        if args.api_key:
            os.environ["RIGHTNOW_API_KEY"] = args.api_key
            os.environ["EVIDRA_PROVIDER"] = args.provider or "rightnow"
        elif args.provider:
            os.environ["EVIDRA_PROVIDER"] = args.provider

        from .db import Database, Document, Passage
        from .documents import extract_text, split_text
        from .pipeline import execute

        print(f"Ingesting '{doc_path.name}'...")
        content = doc_path.read_bytes()
        extracted = extract_text(doc_path.name, content)
        chunks = split_text(extracted.text)

        passages = [
            Passage(id=str(i + 1), document_id="cli-doc", locator=f"Section {i + 1}", text=chunk)
            for i, chunk in enumerate(chunks)
        ]

        print(f"Interrogating document with {len(passages)} passages...")
        result = execute(args.question, passages, guarded=True)

        print("\n" + "=" * 50)
        print("VOXDOC ANSWER:")
        print("=" * 50)
        print(result.get("answer") or result.get("reason", "No answer found."))
        print("\nCITATIONS / EVIDENCE:")
        for ev in result.get("evidence", []):
            print(f"[{ev['id']}] {ev['locator']}: {ev['text']}")
        print("=" * 50)

    elif args.command == "memory":
        from .db import Database
        from .memory import memory_graph_summary

        db = Database()
        with db.session() as session:
            summary = memory_graph_summary(session)
            print("\n" + "=" * 50)
            print("VOXDOC COMPOUNDING MEMORY GRAPH")
            print("=" * 50)
            print(f"Total Knowledge Nodes: {summary['node_count']}")
            print(f"Total Relational Edges: {summary['edge_count']}")
            print(f"Total Reinforced Executions: {summary['total_reinforced_executions']}")
            print(f"Active Domains: {', '.join(summary['domains']) if summary['domains'] else 'None'}")
            if summary["nodes"]:
                print("\nTop Crystallized Concepts:")
                for node in summary["nodes"]:
                    print(f"  • {node['concept']} ({node['executions']} executions, confidence: {node['confidence']:.2f})")
            print("=" * 50 + "\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
