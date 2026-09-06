"""Command-line entry points for evaluation, graph analysis and opt-in generation."""

import argparse
import json
from pathlib import Path
import sys

from .evaluation import compare
from .graph import build_graph
from .io import read_json, save_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    evaluate = commands.add_parser("evaluate", help="offline metrics for all three evaluation strategies")
    evaluate.add_argument("input", type=Path)
    graph = commands.add_parser("graph", help="offline k-core neighborhood as JSON")
    graph.add_argument("input", type=Path)
    graph.add_argument("--labels", choices=("reference", "selected"), default="reference")
    graph.add_argument("--k", type=int, default=2)
    graph.add_argument("--hops", type=int, default=2)
    graph.add_argument("--seed")
    generate = commands.add_parser("generate", help="paid API calls only with explicit opt-in")
    generate.add_argument("input", type=Path)
    generate.add_argument("--output", type=Path, default=Path("outputs/predictions.json"))
    generate.add_argument("--limit", type=int, default=1)
    generate.add_argument("--model", required=True)
    generate.add_argument("--endpoint", default="https://api.openai.com/v1")
    generate.add_argument("--prompt-version", choices=("historical", "corrected"), default="corrected")
    generate.add_argument("--allow-api-calls", action="store_true")
    collector = commands.add_parser("collect", help="explicit network access to ConceptNet")
    collector.add_argument("--max-pages", type=int, default=1)
    collector.add_argument("--output", type=Path, default=Path("outputs/conceptnet.json"))
    args = parser.parse_args()
    try:
        if args.command in ("evaluate", "graph"):
            data = read_json(args.input)
            if "metadata" in data and "data" in data:
                data = data["data"]
            result = compare(data) if args.command == "evaluate" else build_graph(data, args.labels, args.k, args.seed, args.hops)
        elif args.command == "generate":
            if not args.allow_api_calls:
                raise ValueError("Generation can incur API charges; pass --allow-api-calls to opt in")
            from .runner import make_client, run_generation
            complete = make_client(args.model, args.endpoint)
            checkpoint = run_generation(args.input, args.output, complete, args.model, args.endpoint, args.limit, args.prompt_version)
            result = {"output": str(args.output), "records": sum(map(len, checkpoint["data"].values()))}
        else:
            if args.output.exists():
                raise ValueError("Collection output exists; choose a new path")
            from .collector import collect
            data = collect(args.max_pages)
            save_json(args.output, data)
            result = {"output": str(args.output), "counts": {r: len(v) for r, v in data.items()}}
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, ImportError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
