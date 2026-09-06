"""Opt-in API execution; no network operations occur on import."""

import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse

from .evaluation import RELATIONS, records
from .generation import classify, compose_prompt
from .io import read_json, save_json


def run_generation(input_path, output_path, complete, model, endpoint,
                   limit=1, version="corrected"):
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer per relation")
    input_path, output_path = Path(input_path), Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output must not overwrite input")
    data = read_json(input_path)
    list(records(data))
    metadata = dict(input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
                    model=model, endpoint=endpoint, limit_per_relation=limit,
                    prompt_version=version, sampling_policy="three-samples-one-tiebreak",
                    prompt_template_sha256=hashlib.sha256(compose_prompt("A", "B", version=version).encode()).hexdigest())
    checkpoint = dict(metadata=metadata, data={rel: [] for rel in data})
    if output_path.exists():
        checkpoint = read_json(output_path)
        if checkpoint.get("metadata") != metadata or set(checkpoint.get("data", {})) != set(data):
            raise ValueError("Existing output is not a compatible checkpoint; choose another path")
        list(records(checkpoint["data"]))
    for rel in data:
        selected = data[rel][:limit]
        previous = checkpoint["data"][rel]
        if len(previous) > len(selected):
            raise ValueError("Checkpoint exceeds the configured input prefix")
        for old, expected in zip(previous, selected):
            if old["start"] != expected["start"] or old["end"] != expected["end"]:
                raise ValueError("Checkpoint record order does not match input")
    for rel in data:
        for row in data[rel][len(checkpoint["data"][rel]):limit]:
            result = classify(row["start"]["label"], row["end"]["label"], complete, version)
            checkpoint["data"][rel].append(dict(start=row["start"], end=row["end"], **result))
            save_json(output_path, checkpoint)
    return checkpoint


def make_client(model, endpoint):
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("The API endpoint must be an HTTPS URL without credentials or query parameters")
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or key == "xxx":
        raise ValueError("Set OPENAI_API_KEY locally; the placeholder is not a credential")
    if not model.strip():
        raise ValueError("A model name is required")
    from openai import OpenAI
    client = OpenAI(api_key=key, base_url=endpoint, timeout=30, max_retries=0)

    def complete(prompt):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as exc:
            # Do not print server payloads, headers or credentials.
            raise RuntimeError(f"Model request failed ({type(exc).__name__}); completed records remain checkpointed") from None
    return complete
