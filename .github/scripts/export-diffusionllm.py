#!/usr/bin/env python3
"""Export the saved experiment dashboards and their report dependencies for Pages.

Only this export is adapted for publication. Original evidence stays untouched.
Uses the standard library so the export can be repeated without extra packages.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo


ROOT_PAGES = {'dashboard-simple.html', 'dashboard.html'}
EXACT_FILES = {'newton/results/newton-test-1455428.out'}
EXTENSIONS = {'.html', '.htm', '.json', '.jsonl', '.txt', '.md', '.csv',
              '.png', '.jpg', '.jpeg', '.svg', '.css', '.js', '.pdf'}
BINARY = {'.png', '.jpg', '.jpeg', '.pdf'}
MAX_FILE_BYTES = 50 * 1024 * 1024
SKIP_NAMES = {'train.jsonl', 'train.json', 'training-history.json',
              'events.rank0.jsonl', 'README.local.txt'}
PRIVATE_FIELDS = {'password', 'passwd', 'api_key', 'access_token', 'auth_token',
                  'authorization', 'cookie', 'private_key', 'ssh_key', 'secret'}
SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----'),
    re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    re.compile(r'\b(?:sk-proj-|sk-ant-)[A-Za-z0-9_-]{20,}\b'),
    re.compile(r'\bhf_[A-Za-z0-9]{20,}\b'),
    re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
]


def local_target(source: str, href: str) -> str | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path)))


def public_external(href: str) -> bool:
    parsed = urlsplit(href)
    if parsed.scheme == 'data':
        return href.startswith('data:image/')
    return parsed.scheme in ('https', 'http', 'mailto') and not (
        parsed.hostname == 'ood-newton.cs.technion.ac.il'
        or '/home/' in parsed.path or parsed.username or parsed.password)


class Document(HTMLParser):
    """Collect actual HTML links, IDs and experiment rows, ignoring script strings."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.links = []
        self.ids = set()
        self.runs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.links.extend((key, value) for key, value in attrs
                          if key in ('href', 'src', 'poster') and value)
        if values.get('id'):
            self.ids.add(values['id'])
        if values.get('data-run-id'):
            self.runs.append(values['data-run-id'])


class PublicHTML(HTMLParser):
    """Preserve reports while turning unavailable downloads into labelled text."""
    def __init__(self, source, included):
        super().__init__(convert_charrefs=False)
        self.source, self.included = source, included
        self.output = []
        self.anchor_stack = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        href = values.get('href', '')
        target = local_target(self.source, href) if href else None
        blocked = bool(href) and (
            (target is not None and target not in self.included)
            or (urlsplit(href).scheme and not public_external(href)))
        if tag == 'a':
            self.anchor_stack.append(blocked)
            if blocked:
                self.output.append('<span class="local-artifact" title="Retained in the research workspace; not included in this public export">')
                return
        self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor_stack:
            if self.anchor_stack.pop():
                self.output.append(' <small>(local file)</small></span>')
                return
        self.output.append(f'</{tag}>')

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f'&{name};')

    def handle_charref(self, name):
        self.output.append(f'&#{name};')

    def handle_comment(self, data):
        self.output.append(f'<!--{data}-->')

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')


def redact(text: str, root: Path) -> str:
    # Keep run/checkpoint names and hashes, removing personal machine locations.
    text = text.replace(str(root), '[workspace]')
    text = re.sub(r'/Users/[^/\s<>"\'\\]+', '[local-home]', text)
    text = re.sub(r'/home/[^/\s<>"\'\\]+', '[cluster-home]', text)
    text = re.sub(r'\b[A-Za-z0-9._-]+@(?:[A-Za-z0-9.-]+\.)?cs\.technion\.ac\.il\b',
                  '[cluster-login]', text)
    # Session credentials must never become public report content.
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ValueError('Credential-like content found; public export stopped')
    return text


def omit_private_fields(value):
    if isinstance(value, dict):
        return {key: omit_private_fields(item) for key, item in value.items()
                if key.lower() not in PRIVATE_FIELDS}
    if isinstance(value, list):
        return [omit_private_fields(item) for item in value]
    return value


def prepare_dashboard(source: str, text: str) -> str:
    if source == 'dashboard.html':
        # These sections are local operational tools, not experimental results.
        for section in ('cluster', 'files'):
            text, n = re.subn(rf'<section id="{section}">.*?</section>', '', text, flags=re.S)
            if n != 1:
                raise ValueError(f'Expected one {section} section in detailed dashboard')
            text = re.sub(rf'<a href="#{section}"[^>]*>.*?</a>', '', text, flags=re.S)
        for category in ('cluster', 'training'):
            text = re.sub(rf'<option value="{category}">.*?</option>', '', text)
        text = text.replace('Saved on this Mac', 'Public experiment library')
        text = text.replace('Local library', 'Public library')
        text = text.replace('find the datasets, training files and cluster resources behind them.',
                            'inspect the saved results and experimental settings behind them.')
        text = re.sub(r'<footer>.*?</footer>',
                      '<footer><span>Reports reflect saved evidence, not live cluster status.</span>'
                      '<span><a href="about.html">About this experiment library</a></span></footer>', text, flags=re.S)
    return text


def site_chrome(source: str) -> tuple[str, str]:
    directory = posixpath.dirname(source) or '.'
    home = posixpath.relpath('index.html', directory)
    about = posixpath.relpath('about.html', directory)
    style = '<style>.public-nav{display:flex;flex-wrap:wrap;gap:18px;padding:12px 20px;background:#eaf0e5;color:#245b42;font:12px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;border-bottom:1px solid #d6dfd2}.public-nav a{color:#245b42;text-decoration:none}.public-nav a:hover{text-decoration:underline}.local-artifact{color:#70756f!important;cursor:default}.local-artifact small{font-size:.8em;font-weight:400}body>.public-nav{position:relative;z-index:2}@media(min-width:651px){body:has(>.sidebar)>.public-nav{margin-left:224px}}@media(min-width:651px) and (max-width:1180px){body:has(>.sidebar)>.public-nav{margin-left:198px}}@media(min-width:651px) and (max-width:920px){body:has(>.sidebar)>.public-nav{margin-left:176px}}</style>'
    nav = (f'<nav class="public-nav" aria-label="Experiment library">'
           f'<a href="{home}">← All experiments</a>'
           f'<a href="{about}">About these results</a></nav>')
    return style, nav


def about_page(catalog, timestamp):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>About · LLaDA × TSP</title><style>body{{max-width:760px;margin:60px auto;padding:0 24px;font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#24352d;background:#f7f8f4}}a{{color:#245b42}}h1{{line-height:1.2}}li{{margin:8px 0}}.note{{color:#617064}}</style></head><body><a href="index.html">← All experiments</a><h1>A record of the experiments.</h1><p>This library brings together {catalog['experiment_count']} experiment entries and {catalog['report_count']} primary reports from the LLaDA × TSP research workspace, including fine-tuning, inference, speed studies, checks, and unfinished or cancelled attempts.</p><p>Published snapshot: {escape(timestamp)}. Statuses describe saved evidence; this website does not monitor running jobs.</p><h2>How to read the results</h2><ul><li>TSP20 means a travelling-salesperson problem with 20 cities.</li><li>A complete or valid tour visits every city exactly once and returns to the start. An optimal tour has the shortest reference length.</li><li>Optimal counts use each report’s stated evaluation denominator. Gaps are calculated only over valid tours; no valid tours means the gap is undefined.</li><li>Fine-tuning headlines use final validation results. Prompts, datasets, decoding and scoring differ between experiment families; paired comparisons identify what can be compared.</li><li>The learned TSP head and structured decoder are specific to routing. General-language checks use a different decoding mode.</li></ul><h2>Reports and evidence</h2><p>The report pages, saved answers, scoring evidence and selected experimental settings are included. Large training datasets, model weights, operational scripts and some logs are retained in the research workspace. A “local file” label marks a resource that is not part of this export.</p><p>Personal filesystem locations are replaced in public copies. Numerical results, run identities, hashes and reported completion statuses are preserved. Original files remain in the research workspace.</p><p class="note">This research section has its own direct address on the existing GitHub Pages site.</p><p><a href="dashboard.html">Open the detailed comparison library →</a></p></body></html>'''


def export(root: Path, destination: Path) -> dict:
    root, destination = root.resolve(), destination.resolve()
    if destination == root or root.is_relative_to(destination):
        raise ValueError('Destination must be a dedicated export directory')
    if destination.exists() and not (destination / 'publication.json').is_file():
        raise ValueError('Refusing to replace a directory without this exporter’s publication manifest')
    catalog = json.loads((root / 'dashboard/simple-catalog.json').read_text())
    if catalog['needs_summary'] or catalog['missing_local_files']:
        raise ValueError('Fix the dashboard validation before exporting')
    updated = json.loads((root / 'dashboard/link-validation.json').read_text())['checked_at']
    timestamp = datetime.fromisoformat(updated).astimezone(ZoneInfo('Asia/Jerusalem')).strftime('%d %b %Y, %H:%M %Z')
    raw_catalog = json.loads((root / 'dashboard/catalog.json').read_text())
    included, excluded, html_sources = set(), {}, {}
    source_hashes = {}

    def reason(path):
        f = root / path
        if path.startswith(('/', '../')) or not f.resolve().is_relative_to(root):
            return 'outside research workspace'
        if not f.is_file() or f.is_symlink():
            return 'not a regular local file'
        if path not in ROOT_PAGES | EXACT_FILES and not path.startswith(('experiments/', 'outputs/', 'diagnostics/')):
            return 'local operational resource'
        if any(part.startswith('.') for part in Path(path).parts):
            return 'hidden file'
        if f.suffix.lower() not in EXTENSIONS and path not in EXACT_FILES:
            return 'model, archive, script or log'
        if f.name in SKIP_NAMES or 'logs' in f.parts or 'model-cache' in f.parts:
            return 'training dataset or operational log'
        if f.stat().st_size > MAX_FILE_BYTES:
            return 'large artifact retained locally'
        return None

    queue = sorted(ROOT_PAGES | {link['href'] for row in catalog['experiments'] for link in row['links']})
    # Include links rendered dynamically by the detailed search interface.
    queue += [unquote(item['href']) for item in raw_catalog
              if not item.get('external') and item.get('section') not in ('cluster', 'files')]
    while queue:
        source = queue.pop()
        if source in included or source in excluded:
            continue
        why = reason(source)
        if why:
            excluded[source] = why
            continue
        included.add(source)
        f = root / source
        if f.suffix.lower() not in ('.html', '.htm'):
            continue
        content = prepare_dashboard(source, f.read_text())
        html_sources[source] = content
        document = Document()
        document.feed(content)
        for key, href in document.links:
            target = local_target(source, href)
            if target:
                queue.append(target)

    report_seeds = {link['href'] for row in catalog['experiments'] for link in row['links']
                    if link['href'].endswith('.html')}
    if not report_seeds.issubset(included):
        raise ValueError('A report is missing from the public export')
    public_catalog = []
    for item in raw_catalog:
        href = item['href']
        if ((item.get('external') and public_external(href) and item.get('section') != 'cluster')
                or (not item.get('external') and unquote(href) in included)):
            public_catalog.append(item)
    detailed = html_sources['dashboard.html']
    detailed, n = re.subn(r'(<script id="link-catalog" type="application/json">).*?(</script>)',
        lambda m: m[1] + json.dumps(public_catalog, ensure_ascii=False).replace('<', '\\u003c') + m[2],
        detailed, flags=re.S)
    if n != 1:
        raise ValueError('Missing detailed dashboard search catalog')
    detailed = re.sub(r'All links · \d+', f'All links · {len(public_catalog)}', detailed)
    detailed = re.sub(r'\d+ links in one place', f'{len(public_catalog)} links in one place', detailed)
    html_sources['dashboard.html'] = detailed

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f'.{destination.name}-', dir=destination.parent))
    manifest_files = []
    try:
        available = included | {'index.html', 'about.html'}
        for source in sorted(included):
            src = root / source
            target = temporary / source
            target.parent.mkdir(parents=True, exist_ok=True)
            original = src.read_bytes()
            source_hashes[source] = sha256(original).hexdigest()
            if src.suffix.lower() in BINARY:
                output = original
            else:
                text = html_sources.get(source, original.decode('utf-8'))
                if source in html_sources:
                    parser = PublicHTML(source, available)
                    parser.feed(text)
                    text = ''.join(parser.output)
                    style, nav = site_chrome(source)
                    if re.search(r'<body\b', text):
                        text = text.replace('</head>', style + '</head>', 1)
                        text = re.sub(r'<body\b[^>]*>', lambda m: m[0] + nav, text, count=1)
                    else:
                        # Older reports use valid HTML with implicit head/body tags.
                        text, n = re.subn(r'<(?:main|h1|header)\b',
                                         lambda m: style + nav + m[0], text, count=1)
                        if n != 1:
                            raise ValueError(f'Cannot locate content in {source}')
                text = redact(text, root)
                # Structured evidence must remain machine-readable after redaction.
                if src.suffix == '.json':
                    value = json.loads(text)
                    public_value = omit_private_fields(value)
                    if public_value != value:
                        text = json.dumps(public_value, ensure_ascii=False, indent=2) + '\n'
                elif src.suffix == '.jsonl':
                    lines = []
                    for line in text.splitlines():
                        if line.strip():
                            value = json.loads(line)
                            public_value = omit_private_fields(value)
                            lines.append(line if public_value == value else json.dumps(public_value, ensure_ascii=False))
                    text = '\n'.join(lines) + '\n'
                output = text.encode('utf-8')
            target.write_bytes(output)
            manifest_files.append({'path': source, 'bytes': len(output),
                                   'sha256': sha256(output).hexdigest(),
                                   'source_sha256': source_hashes[source]})
        shutil.copyfile(temporary / 'dashboard-simple.html', temporary / 'index.html')
        (temporary / 'about.html').write_text(about_page(catalog, timestamp))
        (temporary / '.nojekyll').touch()
        verification = verify(temporary, catalog)
        manifest = {
            'schema_version': 1,
            'snapshot_at': updated,
            'exported_at': datetime.now(ZoneInfo('Asia/Jerusalem')).isoformat(),
            'experiment_count': catalog['experiment_count'], 'primary_report_count': catalog['report_count'],
            'status_counts': catalog['counts'], 'html_pages': verification['html_pages'],
            'verified_links': verification['verified_links'],
            'bytes': sum(item['bytes'] for item in manifest_files),
            'files': manifest_files,
            'excluded': [{'path': path, 'reason': why} for path, why in sorted(excluded.items())],
        }
        (temporary / 'publication.json').write_text(json.dumps(manifest, indent=2) + '\n')
        # Detect a dashboard/evidence update racing with the export.
        for source, digest in source_hashes.items():
            if sha256((root / source).read_bytes()).hexdigest() != digest:
                raise ValueError(f'Source changed during export: {source}; repeat the export')
        previous = destination.with_name(f'.{destination.name}-previous')
        if previous.exists():
            raise ValueError('Previous export backup exists; inspect it before proceeding')
        if destination.exists():
            destination.rename(previous)
        try:
            temporary.rename(destination)
        except BaseException:
            if previous.exists():
                previous.rename(destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return {key: value for key, value in manifest.items() if key not in ('files', 'excluded')} | {
            'file_count': len(manifest_files), 'local_only_artifacts': len(excluded),
            'destination': str(destination)}
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def verify(destination: Path, catalog=None):
    pages = {}
    for file in destination.rglob('*.html'):
        document = Document()
        text = file.read_text()
        document.feed(text)
        pages[file.relative_to(destination).as_posix()] = document
        if '/Users/' in text or '/home/' in text:
            raise ValueError(f'Personal filesystem path remains in {file.name}')
    failures, links = [], 0
    for source, document in pages.items():
        for key, href in document.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                if not public_external(href):
                    failures.append((source, 'non-public URL'))
                continue
            target = local_target(source, href) or source
            if target.startswith(('/', '../')) or not (destination / target).is_file():
                failures.append((source, href))
            elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                failures.append((source, href))
            links += 1
    if failures:
        raise ValueError('Broken export links: ' + repr(failures[:15]))
    if catalog:
        expected = [row['id'] for row in catalog['experiments']]
        if Counter(pages['index.html'].runs) != Counter(expected):
            raise ValueError('Published experiment coverage differs from local catalog')
    return {'html_pages': len(pages), 'verified_links': links}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.workspace, args.destination), indent=2))
