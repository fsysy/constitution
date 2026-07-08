#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def load_constitution(home: Path) -> dict:
    if yaml is None:
        raise RuntimeError('PyYAML is required to validate amendments.')
    path = home / 'constitution.yaml'
    if not path.exists():
        raise RuntimeError(f'Missing {path}')
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise RuntimeError('constitution.yaml must contain a mapping')
    return data


def validate_article(article: dict, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(article, dict):
        return [f'{label} is not a mapping']
    missing = sorted(REQUIRED_FIELDS - set(article))
    if missing:
        errors.append(f'{label} missing fields: {", ".join(missing)}')
    if not isinstance(article.get('id'), str) or not article.get('id'):
        errors.append(f'{label} id must be a non-empty string')
    if not isinstance(article.get('rank'), int):
        errors.append(f'{label} rank must be an integer')
    scope = article.get('scope')
    if not isinstance(scope, dict):
        errors.append(f'{label} scope must be a mapping')
    else:
        if not isinstance(scope.get('applies_to'), list):
            errors.append(f'{label} scope.applies_to must be a list')
        if not isinstance(scope.get('excludes'), list):
            errors.append(f'{label} scope.excludes must be a list')
    for field in ['category', 'examples']:
        if not isinstance(article.get(field), list):
            errors.append(f'{label} {field} must be a list')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate proposed constitutional amendment article files.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--article-file', action='append', required=True, dest='article_files', help='YAML or JSON article file. Repeat for multiple files.')
    parser.add_argument('--allow-revise', action='store_true', help='Allow proposed IDs and ranks to replace existing articles with the same ID.')
    args = parser.parse_args()

    try:
        home = resolve_home(args.home)
        constitution = load_constitution(home)
        existing = constitution.get('articles') or []
        if not isinstance(existing, list):
            raise RuntimeError('constitution.yaml articles must be a list')
        proposed = load_articles(args.article_files)
        errors: list[str] = []

        proposed_ids: list[str] = []
        proposed_ranks: list[int] = []
        for i, article in enumerate(proposed, 1):
            errors.extend(validate_article(article, f'proposed article {i}'))
            if isinstance(article, dict):
                proposed_ids.append(article.get('id'))
                proposed_ranks.append(article.get('rank'))

        for value in sorted({x for x in proposed_ids if proposed_ids.count(x) > 1}):
            errors.append(f'duplicate proposed article id: {value}')
        for value in sorted({x for x in proposed_ranks if proposed_ranks.count(x) > 1}):
            errors.append(f'duplicate proposed article rank: {value}')

        existing_by_id = {a.get('id'): a for a in existing if isinstance(a, dict)}
        existing_rank_owner = {a.get('rank'): a.get('id') for a in existing if isinstance(a, dict)}
        for article in proposed:
            if not isinstance(article, dict):
                continue
            article_id = article.get('id')
            rank = article.get('rank')
            if article_id in existing_by_id and not args.allow_revise:
                errors.append(f'article id already exists: {article_id} (use --allow-revise to replace it)')
            rank_owner = existing_rank_owner.get(rank)
            if rank_owner and rank_owner != article_id:
                errors.append(f'rank {rank} is already used by {rank_owner}')

        if errors:
            for error in errors:
                print(f'ERROR: {error}')
            return 1

        print(f'OK: {len(proposed)} proposed article(s) validated')
        return 0
    except Exception as exc:
        print(f'ERROR: {exc}')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
