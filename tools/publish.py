#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

import markdown as md

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif', '.bmp', '.tif', '.tiff'}
MARKDOWN_EXTS = {'.md', '.markdown'}
GENERIC_STEMS = {'translation', 'delivery', 'readme', 'index', 'notes', 'note'}


def run(cmd: List[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout.strip()


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKC', text).strip().lower()
    text = text.replace('—', '-').replace('–', '-')
    text = re.sub(r'[\\/]+', '-', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^0-9a-z\u4e00-\u9fff._-]+', '-', text)
    text = re.sub(r'-{2,}', '-', text).strip('-._')
    if not text:
        text = 'item-' + hashlib.sha1(text.encode('utf-8')).hexdigest()[:10]
    return text


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def split_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith('---\n'):
        return {}, text
    parts = text.split('\n---\n', 1)
    if len(parts) != 2:
        return {}, text
    raw = parts[0][4:]
    body = parts[1]
    meta: Dict[str, str] = {}
    for line in raw.splitlines():
        m = re.match(r'([A-Za-z0-9_-]+):\s*(.*)', line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith(('"', "'")) and value.endswith(('"', "'")) and len(value) >= 2:
            value = value[1:-1]
        meta[key] = value
    return meta, body


def title_from_markdown(body: str, fallback: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s.startswith('# '):
            return s[2:].strip()
    return fallback


def derive_slug(source: Path, workspace: Path) -> str:
    try:
        rel = source.resolve().relative_to(workspace.resolve())
        base = str(rel.with_suffix(''))
    except Exception:
        base = source.stem
    if source.stem.lower() in GENERIC_STEMS and source.parent.name:
        base = f"{source.parent.name}-{source.stem}"
    slug = slugify(base)
    if len(slug) > 90:
        digest = hashlib.sha1(str(source).encode('utf-8')).hexdigest()[:8]
        slug = slug[:80].rstrip('-') + '-' + digest
    return slug


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_local_assets(text: str, source_dir: Path, assets_dir: Path) -> str:
    ensure_dir(assets_dir)

    def replace_md_image(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2).strip()
        new_target = rewrite_target(target, source_dir, assets_dir)
        return f'![{label}]({new_target})'

    def replace_html_img(match: re.Match[str]) -> str:
        before, target, after = match.group(1), match.group(2).strip(), match.group(3)
        new_target = rewrite_target(target, source_dir, assets_dir)
        return f'{before}{new_target}{after}'

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_image, text)
    text = re.sub(r'(<img[^>]*src=["\'])([^"\']+)(["\'][^>]*>)', replace_html_img, text, flags=re.IGNORECASE)
    return text


def rewrite_target(target: str, source_dir: Path, assets_dir: Path) -> str:
    clean = target.split(' ')[0].strip()
    if re.match(r'^(https?:|data:|#)', clean, re.IGNORECASE):
        return target
    if clean.startswith('/'):
        return target
    source = (source_dir / clean).resolve()
    if not source.exists() or not source.is_file():
        return target
    name = source.name
    dest = assets_dir / name
    if dest.exists() and dest.read_bytes() == source.read_bytes():
        return target.replace(clean, f'./assets/{name}')
    if dest.exists() and dest.read_bytes() != source.read_bytes():
        stem, suffix = source.stem, source.suffix
        digest = hashlib.sha1(source.read_bytes()).hexdigest()[:8]
        name = f'{stem}-{digest}{suffix}'
        dest = assets_dir / name
    shutil.copy2(source, dest)
    return target.replace(clean, f'./assets/{name}')


def render_markdown_html(text: str) -> str:
    renderer = md.Markdown(extensions=['extra', 'fenced_code', 'tables', 'toc', 'sane_lists'])
    html_body = renderer.convert(text)
    return html_body


def excerpt_from_text(text: str, limit: int = 180) -> str:
    plain = re.sub(r'```[\s\S]*?```', ' ', text)
    plain = re.sub(r'`([^`]+)`', r'\1', plain)
    plain = re.sub(r'!\[[^\]]*\]\([^)]+\)', ' ', plain)
    plain = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain)
    plain = re.sub(r'[#>*_\-]+', ' ', plain)
    plain = re.sub(r'\s+', ' ', plain).strip()
    return plain[:limit].rstrip() + ('…' if len(plain) > limit else '')


def article_page(title: str, body_html: str, source_display: str, updated_at: str) -> str:
    safe_title = html.escape(title)
    source_display = html.escape(source_display)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
  <div class="article">
    <div class="topbar"><div class="brand"><a href="../../index.html">NotebookLM Sources</a></div></div>
    <div class="article-wrap">
      <div class="kicker">Published for NotebookLM · GitHub Pages</div>
      <div class="note">Updated {html.escape(updated_at)}</div>
      <div class="source-pill">Source: {source_display}</div>
      <hr>
      <article class="article-body article">{body_html}</article>
    </div>
    <div class="footer">Static page generated from local content.</div>
  </div>
</body>
</html>
'''


def image_page(title: str, image_name: str, source_display: str, updated_at: str) -> str:
    safe_title = html.escape(title)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
  <div class="article">
    <div class="topbar"><div class="brand"><a href="../../index.html">NotebookLM Sources</a></div></div>
    <div class="article-wrap viewer">
      <div class="kicker">Image artifact · GitHub Pages</div>
      <h1>{safe_title}</h1>
      <div class="note">Updated {html.escape(updated_at)}</div>
      <div class="source-pill">Source: {html.escape(source_display)}</div>
      <hr>
      <img src="./assets/{html.escape(image_name)}" alt="{safe_title}">
    </div>
    <div class="footer">Static page generated from local content.</div>
  </div>
</body>
</html>
'''


def index_page(entries: List[Dict[str, str]]) -> str:
    cards = []
    for entry in entries:
        excerpt = html.escape(entry.get('excerpt', ''))
        title = html.escape(entry['title'])
        url = html.escape(entry['url'])
        source = html.escape(entry['source'])
        updated = html.escape(entry['updated_at'])
        kind = html.escape(entry['kind'])
        cards.append(f'''<a class="card" href="{url}">
  <div class="meta"><span>{kind}</span><span>{updated}</span><span>{source}</span></div>
  <h2>{title}</h2>
  <div class="excerpt">{excerpt}</div>
</a>''')
    cards_html = '\n'.join(cards) if cards else '<div class="empty">No published entries yet.</div>'
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NotebookLM Sources</title>
  <link rel="stylesheet" href="./assets/style.css">
</head>
<body>
  <div class="shell">
    <div class="topbar"><div class="brand">GitHub Pages · NotebookLM Sources</div></div>
    <section class="hero">
      <h1>NotebookLM Sources</h1>
      <p>Clean public pages generated from local Markdown and image artifacts, ready to paste into NotebookLM as web URLs.</p>
    </section>
    <section class="grid">{cards_html}</section>
    <div class="footer">Generated from the local publishing workflow.</div>
  </div>
</body>
</html>
'''


def load_manifest(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding='utf-8'))


def save_manifest(path: Path, entries: List[Dict[str, str]]) -> None:
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git_commit_push(repo: Path, message: str) -> None:
    run(['git', 'add', '.'], cwd=repo)
    status = run(['git', 'status', '--porcelain'], cwd=repo)
    if not status.strip():
        return
    run(['git', 'commit', '-m', message], cwd=repo)
    run(['git', 'push', 'origin', 'main'], cwd=repo)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('--repo', required=True)
    parser.add_argument('--title')
    parser.add_argument('--slug')
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f'source not found: {source}')

    workspace = repo.parent.parent.resolve()
    docs = repo / 'docs'
    posts_dir = docs / 'posts'
    assets_css = docs / 'assets' / 'style.css'
    manifest_path = repo / 'site_data' / 'posts.json'
    ensure_dir(posts_dir)
    ensure_dir(assets_css.parent)
    ensure_dir(manifest_path.parent)

    slug = args.slug or derive_slug(source, workspace)
    page_dir = posts_dir / slug
    assets_dir = page_dir / 'assets'
    ensure_dir(page_dir)
    ensure_dir(assets_dir)

    now = dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')
    source_display = str(source.relative_to(workspace)) if source.is_relative_to(workspace) else str(source)

    if source.suffix.lower() in MARKDOWN_EXTS:
        raw = read_text(source)
        meta, body = split_front_matter(raw)
        title = args.title or meta.get('title') or title_from_markdown(body, source.stem)
        body = copy_local_assets(body, source.parent, assets_dir)
        html_body = render_markdown_html(body)
        page_html = article_page(title, html_body, source_display, now)
        excerpt = excerpt_from_text(body)
        kind = 'markdown'
    elif source.suffix.lower() in IMAGE_EXTS:
        title = args.title or source.stem
        dest_image = assets_dir / source.name
        shutil.copy2(source, dest_image)
        page_html = image_page(title, source.name, source_display, now)
        excerpt = 'Image artifact published as a simple static page.'
        kind = 'image'
    else:
        raise SystemExit(f'unsupported source type: {source.suffix}')

    (page_dir / 'index.html').write_text(page_html, encoding='utf-8')

    entries = load_manifest(manifest_path)
    url = f'./posts/{slug}/index.html'
    updated_entry = {
        'slug': slug,
        'title': title,
        'source': source_display,
        'updated_at': now,
        'url': url,
        'excerpt': excerpt,
        'kind': kind,
    }
    found = False
    for i, entry in enumerate(entries):
        if entry.get('slug') == slug:
            entries[i] = updated_entry
            found = True
            break
    if not found:
        entries.append(updated_entry)
    entries.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    save_manifest(manifest_path, entries)
    (docs / 'index.html').write_text(index_page(entries), encoding='utf-8')
    (docs / '.nojekyll').write_text('\n', encoding='utf-8')

    git_commit_push(repo, f"Publish {title}")

    owner_repo = run(['git', 'config', '--get', 'remote.origin.url'], cwd=repo)
    m = re.search(r'github.com[:/]([^/]+)/([^/.]+)(?:\.git)?$', owner_repo)
    if m:
        owner, repo_name = m.group(1), m.group(2)
        public_url = f'https://{owner}.github.io/{repo_name}/posts/{slug}/'
        print(public_url)
    else:
        print(f'published slug: {slug}')


if __name__ == '__main__':
    main()
