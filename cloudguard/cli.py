import argparse
import json
from pathlib import Path
from .scanner import scan
from .retrieval import retrieve
from .probe import probe
from .llm import audit
from .pipeline import run


def main():
    parser = argparse.ArgumentParser(description="Active Cloud Guard research CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan")
    s.add_argument("path")
    r = sub.add_parser("retrieve")
    r.add_argument("query")
    r.add_argument("--kb", default="knowledge/sources.json")
    a = sub.add_parser("audit")
    a.add_argument("path")
    a.add_argument("--model", required=True)
    a.add_argument("--kb", default="knowledge/sources.json")
    p = sub.add_parser("probe")
    p.add_argument("--inventory", required=True)
    p.add_argument("--asset", required=True)
    e = sub.add_parser("run")
    e.add_argument("path")
    e.add_argument("--kb", default="knowledge/sources.json")
    e.add_argument("--inventory")
    e.add_argument("--model")
    e.add_argument("--vector-index")
    v = sub.add_parser("index")
    v.add_argument("--kb", default="knowledge/sources.json")
    v.add_argument("--index", default="output/chroma")
    v = sub.add_parser("vector-retrieve")
    v.add_argument("query")
    v.add_argument("--kb", default="knowledge/sources.json")
    v.add_argument("--index", default="output/chroma")
    args = parser.parse_args()
    try:
        if args.command == "scan":
            result = scan(args.path)
        elif args.command == "retrieve":
            result = retrieve(args.query, args.kb)
        elif args.command == "audit":
            text = Path(args.path).read_text(encoding="utf-8")
            result = audit(text, retrieve(text, args.kb), args.model)
        elif args.command == "run":
            result = run(
                args.path, args.kb, args.inventory, args.model, args.vector_index
            )
        elif args.command == "index":
            from .vector import index

            result = index(args.kb, args.index)
        elif args.command == "vector-retrieve":
            from .vector import retrieve_vector

            result = retrieve_vector(args.query, args.kb, args.index)
        else:
            inventory = json.loads(Path(args.inventory).read_text())
            entries = [e for e in inventory if e["asset_id"] == args.asset]
            if len(entries) != 1:
                raise ValueError(
                    "asset must have exactly one explicit inventory endpoint"
                )
            e = entries[0]
            result = probe(
                e["host"],
                e["port"],
                allowlist={(e["host"], e["port"])},
                asset_id=e["asset_id"],
            )
        print(json.dumps(result, indent=2))
    except Exception as error:
        parser.exit(
            2, f"ERROR ({type(error).__name__}): operation failed; no clean verdict.\n"
        )


if __name__ == "__main__":
    main()
