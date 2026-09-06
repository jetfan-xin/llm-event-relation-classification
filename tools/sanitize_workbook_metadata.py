"""Remove only Excel's absolute save-path element, without rewriting worksheets.

Uses ZIP/XML container processing, not spreadsheet authoring. All ZIP members
other than xl/workbook.xml retain their exact uncompressed bytes.
"""

import argparse
from pathlib import Path
import re
from zipfile import ZipFile
from xml.etree import ElementTree


def redact_absolute_path(content):
    cleaned, count = re.subn(rb'<x15ac:absPath\b[^>]*/>', b'', content)
    if count != 1:
        raise ValueError('Expected exactly one absolute save-path element')
    ElementTree.fromstring(cleaned)
    return cleaned


def sanitize(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Never overwrite the source workbook')
    if destination.exists():
        raise FileExistsError(destination)
    with ZipFile(source) as original:
        cleaned = redact_absolute_path(original.read('xl/workbook.xml'))
        destination.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(destination, 'x') as published:
            for info in original.infolist():
                content = cleaned if info.filename == 'xl/workbook.xml' else original.read(info.filename)
                published.writestr(info, content)
    with ZipFile(source) as original, ZipFile(destination) as published:
        assert original.namelist() == published.namelist()
        for name in original.namelist():
            expected = cleaned if name == 'xl/workbook.xml' else original.read(name)
            assert published.read(name) == expected, name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    sanitize(args.source, args.destination)
    print('Removed one absolute save-path element; all other ZIP member contents unchanged.')
