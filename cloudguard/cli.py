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
    a.add_argument("--cache-dir")
    a.add_argument("--timeout", type=float, default=180)
    a.add_argument("--max-tokens", type=int, default=512)
    p = sub.add_parser("probe")
    p.add_argument("--inventory", required=True)
    p.add_argument("--asset", required=True)
    e = sub.add_parser("run")
    e.add_argument("path")
    e.add_argument("--kb", default="knowledge/sources.json")
    e.add_argument("--inventory")
    e.add_argument("--model")
    e.add_argument("--vector-index")
    e.add_argument("--cache-dir")
    e.add_argument("--timeout", type=float, default=180)
    e.add_argument("--max-tokens", type=int, default=512)
    e.add_argument("--policy", help="Hash-bound operator reachability policy JSON")
    e.add_argument("--reviews", help="Hash-bound human candidate approvals JSON")
    v = sub.add_parser("index")
    v.add_argument("--kb", default="knowledge/sources.json")
    v.add_argument("--index", default="output/chroma")
    v.add_argument("--force", action="store_true")
    v = sub.add_parser("vector-retrieve")
    v.add_argument("query")
    v.add_argument("--kb", default="knowledge/sources.json")
    v.add_argument("--index", default="output/chroma")
    sv = sub.add_parser(
        "verify-service",
        help="Read-only Compose identity and credential-free protocol check",
    )
    sv.add_argument(
        "path", help="Actual deployed Compose file, not a synthetic analogue"
    )
    sv.add_argument("--inventory", required=True)
    sv.add_argument("--service", choices=["redis", "postgres"], required=True)
    rt = sub.add_parser(
        "runtime-replay", help="Observation-only Engine 2 normalized-event replay"
    )
    rt.add_argument("path", help="Observation capture JSON")
    rt.add_argument(
        "--baseline",
        action="append",
        required=True,
        help="Separate baseline capture; repeat for multiple captures",
    )
    rt.add_argument("--inventory", required=True)
    rt.add_argument("--window-seconds", type=int, default=60)
    rt.add_argument("--threshold", type=float, default=3.0)
    ir = sub.add_parser(
        "integrated-replay", help="Offline configuration and saved-runtime context"
    )
    ir.add_argument("configuration")
    ir.add_argument("observation")
    ir.add_argument("--baseline", action="append", required=True)
    ir.add_argument("--inventory", required=True)
    ir.add_argument("--window-seconds", type=int, default=60)
    ir.add_argument("--threshold", type=float, default=3.0)
    ir.add_argument("--runtime-ml", choices=["isolation-forest", "autoencoder", "both"])
    ir.add_argument(
        "--measure-stages",
        action="store_true",
        help="Record local wall/process CPU cost, not sensor overhead or energy",
    )
    ir.add_argument(
        "--engine1-pipeline",
        action="store_true",
        help="Run the existing Engine1 pipeline; explicit model/probe stages may access local services",
    )
    ir.add_argument("--kb")
    ir.add_argument("--model")
    ir.add_argument("--vector-index")
    ir.add_argument("--cache-dir")
    ir.add_argument("--timeout", type=float, default=180)
    ir.add_argument("--max-tokens", type=int, default=512)
    ir.add_argument("--policy")
    ir.add_argument("--reviews")
    args = parser.parse_args()
    try:
        if args.command == "scan":
            result = scan(args.path)
        elif args.command == "retrieve":
            result = retrieve(args.query, args.kb)
        elif args.command == "audit":
            text = Path(args.path).read_text(encoding="utf-8")
            result = audit(
                text,
                retrieve(text, args.kb),
                args.model,
                cache_dir=args.cache_dir,
                timeout=args.timeout,
                max_tokens=args.max_tokens,
            )
        elif args.command == "run":
            result = run(
                args.path,
                args.kb,
                args.inventory,
                args.model,
                args.vector_index,
                policy=args.policy,
                reviews=args.reviews,
                cache_dir=args.cache_dir,
                timeout=args.timeout,
                max_tokens=args.max_tokens,
            )
        elif args.command == "index":
            from .vector import index

            result = index(args.kb, args.index, force=args.force)
        elif args.command == "vector-retrieve":
            from .vector import retrieve_vector

            result = retrieve_vector(args.query, args.kb, args.index)
        elif args.command == "runtime-replay":
            from .runtime import analyze

            result = analyze(
                args.baseline,
                args.path,
                args.inventory,
                window_seconds=args.window_seconds,
                threshold=args.threshold,
            )
        elif args.command == "integrated-replay":
            from .integration import replay

            result = replay(
                args.configuration,
                args.baseline,
                args.observation,
                args.inventory,
                window_seconds=args.window_seconds,
                threshold=args.threshold,
                engine1_pipeline=args.engine1_pipeline,
                runtime_ml=args.runtime_ml,
                measure_stages=args.measure_stages,
                kb=args.kb,
                model=args.model,
                vector_index=args.vector_index,
                cache_dir=args.cache_dir,
                timeout=args.timeout,
                max_tokens=args.max_tokens,
                policy=args.policy,
                reviews=args.reviews,
            )
        elif args.command == "verify-service":
            from .service_probe import verify_service

            result = verify_service(args.path, args.inventory, args.service)
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
