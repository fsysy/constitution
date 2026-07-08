#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


REQUIRED_FIELDS = {'id', 'rank', 'title', 'text', 'scope', 'category', 'rationale', 'examples', 'status', 'created_at', 'amended_at'}


def resolve_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    env_value = os.environ.get('AGENT_CONSTITUTION_HOME')
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path.home() / '.agent-constitution'


def load_structured(path: Path) -> object:
    text = path.read_text(encoding='utf-8')
    if path.suffix.lower() == '.json':
        return json.loads(text)
    if yaml is None:
        raise RuntimeError('PyYAML is required to read YAML amendment files.')
    return yaml.safe_load(text)


def load_articles(paths: list[str]) -> list[dict]:
    articles: list[dict] = []
    for raw_path in paths:
        data = load_structured(Path(raw_path).expanduser())
        if isinstance(data, dict) and isinstance(data.get('articles'), list):
            articles.extend(data['articles'])
        elif isinstance(data, dict):
            articles.append(data)
        elif isinstance(data, list):
            articles.extend(data)
        else:
            raise RuntimeError(f'Unsupported amendment document shape: {raw_path}')
    return articles


def validate_article(article: dict, label: str) -> None:
    if not isinstance(article, dict):
        raise RuntimeError(f'{label} is not a mapping')
    missing = sorted(REQUIRED_FIELDS - set(article))
    if missing:
        raise RuntimeError(f'{label} missing fields: {", ".join(missing)}')
    if not isinstance(article.get('id'), str) or not article.get('id'):
        raise RuntimeError(f'{label} id must be a non-empty string')
    if not isinstance(article.get('rank'), int):
        raise RuntimeError(f'{label} rank must be an integer')


def render_markdown(data: dict) -> str:
    lines = [
        '# Agent Constitution',
        '',
        'Canonical source: `constitution.yaml`',
        '',
        f"Constitution version: `{data.get('constitution_version', 'unknown')}`",
        '',
    ]
    articles = data.get('articles') or []
    for article in sorted(articles, key=lambda item: item.get('rank', 999999)):
        lines.extend([
            f"## {article.get('id')}. {article.get('title')}",
            '',
            f"Rank: {article.get('rank')}",
            '',
            str(article.get('text', '')),
            '',
            f"Scope: `{', '.join(article.get('scope', {}).get('applies_to', []))}`",
            '',
            f"Category: `{', '.join(article.get('category', []))}`",
            '',
            f"Rationale: {article.get('rationale', '')}",
            '',
        ])
    return '\n'.join(lines)


def load_json(path: Path, fallback: dict) -> dict:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Apply approved constitutional amendment articles.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--article-file', action='append', required=True, dest='article_files', help='YAML or JSON article file. Repeat for multiple files.')
    parser.add_argument('--summary', required=True, help='User request or amendment summary.')
    parser.add_argument('--approval', required=True, help='Explicit approval statement from the user.')
    parser.add_argument('--amendment-id', help='Optional amendment ID. Defaults to A-YYYY-MM-DD-NNN.')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    try:
        if yaml is None:
            raise RuntimeError('PyYAML is required to apply amendments.')

        home = resolve_home(args.home)
        yaml_path = home / 'constitution.yaml'
        md_path = home / 'constitution.md'
        index_path = home / 'index.json'
        amendments_dir = home / 'logs' / 'amendments'
        data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise RuntimeError('constitution.yaml must contain a mapping')
        existing = data.get('articles') or []
        if not isinstance(existing, list):
            raise RuntimeError('constitution.yaml articles must be a list')

        proposed = load_articles(args.article_files)
        for i, article in enumerate(proposed, 1):
            validate_article(article, f'proposed article {i}')

        by_id = {article['id']: article for article in existing if isinstance(article, dict) and article.get('id')}
        prior_articles = {article['id']: article for article in existing if isinstance(article, dict) and article.get('id')}
        changed_ids: list[str] = []
        for article in proposed:
            rank_owner = next((item.get('id') for item in by_id.values() if item.get('rank') == article['rank'] and item.get('id') != article['id']), None)
            if rank_owner:
                raise RuntimeError(f"rank {article['rank']} is already used by {rank_owner}")
            by_id[article['id']] = article
            changed_ids.append(article['id'])

        data['articles'] = sorted(by_id.values(), key=lambda item: item.get('rank', 999999))
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        today = now.date().isoformat()
        amendment_id = args.amendment_id
        if not amendment_id:
            amendments_dir.mkdir(parents=True, exist_ok=True)
            prefix = f'A-{today}-'
            highest = 0
            for path in amendments_dir.glob(f'{prefix}*.json'):
                suffix = path.stem.removeprefix(prefix)
                if suffix.isdigit():
                    highest = max(highest, int(suffix))
            amendment_id = f'{prefix}{highest + 1:03d}'

        log = {
            'amendment_id': amendment_id,
            'created_at': now.isoformat().replace('+00:00', 'Z'),
            'summary': args.summary,
            'approval': args.approval,
            'affected_article_ids': changed_ids,
            'prior_articles': {article_id: prior_articles.get(article_id) for article_id in changed_ids},
            'new_articles': {article['id']: article for article in proposed},
            'files_changed': [
                str(yaml_path),
                str(md_path),
                str(amendments_dir / f'{amendment_id}.json'),
            ],
        }

        if args.dry_run:
            print(json.dumps({'dry_run': True, 'amendment': log}, indent=2, sort_keys=True))
            return 0

        yaml_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding='utf-8')
        md_path.write_text(render_markdown(data), encoding='utf-8')
        log_path = amendments_dir / f'{amendment_id}.json'
        write_json(log_path, log)
        index = load_json(index_path, {'judgments': {}, 'amendments': {}})
        index.setdefault('judgments', {})
        index.setdefault('amendments', {})
        index_entry = {
            'amendment_id': amendment_id,
            'path': str(log_path.relative_to(home)),
            'affected_article_ids': changed_ids,
            'created_at': log['created_at'],
        }
        if isinstance(index.get('amendments'), list):
            index['amendments'].append(index_entry)
        elif isinstance(index.get('amendments'), dict):
            index['amendments'][amendment_id] = index_entry
        else:
            index['amendments'] = {amendment_id: index_entry}
        write_json(index_path, index)
        print(json.dumps({'amendment_id': amendment_id, 'log_path': str(log_path), 'affected_article_ids': changed_ids}, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f'ERROR: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
