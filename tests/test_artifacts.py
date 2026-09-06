"""Publication integrity checks for the original saved experiment artifacts."""

from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
from zipfile import ZipFile

from tools.sanitize_workbook_metadata import sanitize
from tools.verify_repository import verify

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'artifacts/original'


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'link'):
            self.urls.extend(value for key, value in attrs if key in ('src', 'href') and value)


class ArtifactTests(unittest.TestCase):
    def test_screenshot_provenance_and_dimensions(self):
        manifest = json.loads((ROOT / 'evidence/screenshots/capture-manifest.json').read_text())
        self.assertEqual(len(manifest['captures']), 5)
        for capture in manifest['captures']:
            source = (ROOT / capture['source']).read_bytes()
            png = (ROOT / capture['image']).read_bytes()
            self.assertEqual(hashlib.sha256(source).hexdigest(), capture['source_sha256'])
            self.assertEqual(hashlib.sha256(png).hexdigest(), capture['image_sha256'])
            self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(int.from_bytes(png[16:20], 'big'), capture['width'])
            self.assertEqual(int.from_bytes(png[20:24], 'big'), capture['height'])
            text = source.decode()
            for name in ('nodes', 'edges'):
                values = json.loads(re.search(r'\b' + name + r'\s*=\s*new vis.DataSet\((\[.*?\])\);', text, re.S).group(1))
                self.assertEqual(len(values), capture[name])

    def test_all_original_project_code_is_published(self):
        manifest = json.loads((ROOT / 'source-manifest.json').read_text())
        code_sources = {s['path'] for s in manifest['sources'] if Path(s['path']).suffix in ('.py', '.ipynb')}
        mapped = set()
        for asset in manifest['published_assets']:
            mapped.add(asset['source'])
            mapped.update(asset.get('equivalent_sources', []))
        self.assertTrue(code_sources)
        self.assertEqual(code_sources - mapped, set())
        self.assertFalse((ROOT / 'archive').exists())

    def test_original_error_analyzer_runs_on_saved_records(self):
        result = subprocess.run(
            [sys.executable, '-B', str(ROOT / 'pipeline/analyzer.py')],
            cwd=ORIGINAL / 'semantic-networks_total/data',
            capture_output=True, text=True, timeout=10, check=True,
        )
        self.assertIn('Find 30 wrong relations', result.stdout)
        self.assertEqual(result.stdout.count('Event Pair:'), 30)

    def test_publication_integrity(self):
        self.assertEqual(verify()['errors'], [])

    def test_saved_graph_sizes(self):
        expected = {
            'semantic-networks/visualizations/Filtered Semantic Network.html': (69, 82),
            'semantic-networks_total/Filtered Semantic Network.html': (69, 82),
            'semantic-networks_total/visualizations/Filtered Semantic Network.html': (194, 246),
            'semantic-networks_total/visualizations/K-core Semantic Network(k=2).html': (278, 353),
            'semantic-networks_total/visualizations/Original Semantic Network of Connected Events.html': (1978, 2064),
        }
        for path, counts in expected.items():
            text = (ORIGINAL / path).read_text()
            arrays = [json.loads(re.search(r'\b' + name + r'\s*=\s*new vis.DataSet\((\[.*?\])\);', text, re.S).group(1))
                      for name in ('nodes', 'edges')]
            self.assertEqual(tuple(map(len, arrays)), counts, path)
            ids = {node['id'] for node in arrays[0]}
            self.assertTrue(all(edge['from'] in ids and edge['to'] in ids for edge in arrays[1]), path)

    def test_html_local_resources_exist(self):
        files = list(ORIGINAL.rglob('*.html'))
        self.assertEqual(len(files), 5)
        for file in files:
            parser = Resources()
            parser.feed(file.read_text())
            self.assertTrue(parser.urls)
            for url in parser.urls:
                if urlsplit(url).scheme or url.startswith('//'):
                    self.assertTrue(url.startswith('https://'))
                    continue
                target = (file.parent / unquote(urlsplit(url).path)).resolve()
                self.assertTrue(target.is_relative_to(ORIGINAL), url)
                self.assertTrue(target.is_file(), url)

    def test_intermediate_record_counts(self):
        data = json.loads((ROOT / 'data/event_pairs.json').read_text())
        self.assertEqual(sum(map(len, data.values())), 10336)
        expected = {
            'generated_relations_progress.json': 820,
            'semantic-networks_total/data/output.json': 10341,
            'semantic-networks_total/data/generated_relations_progress.json': 4000,
            'semantic-networks_total/data/filtered_has_subevent.json': 1340,
            'semantic-networks_total/data/enriched_filtered_data.json': 1340,
            'semantic-networks_total/data/random_relations.json': 30,
        }
        for path, count in expected.items():
            data = json.loads((ORIGINAL / path).read_text())
            self.assertEqual(sum(map(len, data.values())), count, path)

    def test_workbook_structure(self):
        with ZipFile(ORIGINAL / 'semantic-networks/result/Evaluation Scores.xlsx') as workbook:
            self.assertEqual(len([n for n in workbook.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+.xml', n)]), 2)
            for name in workbook.namelist():
                if name.endswith(('.xml', '.rels')):
                    ElementTree.fromstring(workbook.read(name))
            self.assertNotIn(b'x15ac:absPath', workbook.read('xl/workbook.xml'))

    def test_redaction_changes_only_target_member(self):
        with tempfile.TemporaryDirectory() as directory:
            source, destination = Path(directory) / 'source.xlsx', Path(directory) / 'published.xlsx'
            xml = b'<workbook xmlns:x15ac="urn:test"><x15ac:absPath url="private-folder/"/><sheets/></workbook>'
            entries = {'xl/workbook.xml': xml, 'xl/worksheets/sheet1.xml': b'<worksheet/>', 'xl/styles.xml': b'<styleSheet/>'}
            with ZipFile(source, 'x') as workbook:
                for name, data in entries.items():
                    workbook.writestr(name, data)
            original_bytes = source.read_bytes()
            sanitize(source, destination)
            self.assertEqual(source.read_bytes(), original_bytes)
            with ZipFile(destination) as workbook:
                self.assertEqual(workbook.namelist(), list(entries))
                self.assertEqual(workbook.read('xl/workbook.xml'), xml.replace(b'<x15ac:absPath url="private-folder/"/>', b''))
                for name in entries:
                    if name != 'xl/workbook.xml':
                        self.assertEqual(workbook.read(name), entries[name])
            with self.assertRaises(FileExistsError):
                sanitize(source, destination)
            with self.assertRaises(ValueError):
                sanitize(source, source)
