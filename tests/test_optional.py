"""Optional dependencies are exercised in CI without contacting a provider."""

import importlib.util
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("openai", "pyvis"))
if os.environ.get("REQUIRE_OPTIONAL") == "1" and not AVAILABLE:
    raise RuntimeError("Optional integration job requires the optional dependencies")


@unittest.skipUnless(AVAILABLE, "Optional dependencies not installed")
class OptionalTests(unittest.TestCase):
    def test_client_configuration_without_network(self):
        from event_relations.runner import make_client
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-placeholder"}), patch("openai.OpenAI") as constructor:
            constructor.return_value.chat.completions.create.return_value = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"Relation":"Causes","Reason":"test"}'))])
            complete = make_client("gpt-4o", "https://example.invalid/v1")
            self.assertIn("Causes", complete("test prompt"))
            self.assertEqual(constructor.call_args.kwargs["max_retries"], 0)
            self.assertEqual(constructor.call_args.kwargs["timeout"], 30)

    def test_client_rejects_insecure_endpoint(self):
        from event_relations.runner import make_client
        for url in ("http://example.invalid", "https://user:pass@example.invalid", "https://example.invalid?key=test"):
            with self.assertRaises(ValueError):
                make_client("gpt-4o", url)

    def test_interactive_export_escapes_labels(self):
        from event_relations.graph import render_html
        graph = dict(nodes=[dict(id="a", label="<script>bad</script>", degree=1), dict(id="b", label="safe", degree=1)],
                     edges=[dict(source="a", target="b", relation="Causes")])
        html = render_html(graph)
        self.assertIn("vis.Network", html)
        self.assertNotIn("<script>bad</script>", html)
        self.assertIn("Causes", html)


if __name__ == "__main__":
    unittest.main()
