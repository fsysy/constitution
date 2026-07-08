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


def resolve_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    env_value = os.environ.get('AGENT_CONSTITUTION_HOME')
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path.home() / '.agent-constitution'


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate an agent constitution store.')
    parser.add_argument('home', nargs='?', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    args = parser.parse_args()

    if yaml is None:
        print('ERROR: PyYAML is required for validation. Install pyyaml or ask the agent to inspect manually.')
        return 2

    home = resolve_home(args.home)
    yaml_path = home / 'constitution.yaml'
    if not yaml_path.exists():
        print(f'ERROR: missing {yaml_path}')
        return 1

    data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
    errors: list[str] = []
    if not isinstance(data, dict):
        errors.append('constitution.yaml must contain a mapping')
    else:
        if not data.get('constitution_version'):
            errors.append('missing constitution_version')
        articles = data.get('articles')
        if not isinstance(articles, list) or not articles:
            errors.append('articles must be a non-empty list')
        else:
            ids = [a.get('id') for a in articles if isinstance(a, dict)]
            ranks = [a.get('rank') for a in articles if isinstance(a, dict)]
            if len(ids) != len(set(ids)):
                errors.append('duplicate article ids')
            if len(ranks) != len(set(ranks)):
                errors.append('duplicate article ranks')
            required = {'id', 'rank', 'title', 'text', 'scope', 'category', 'rationale', 'examples', 'status', 'created_at', 'amended_at'}
            for i, article in enumerate(articles, 1):
                if not isinstance(article, dict):
                    errors.append(f'article {i} is not a mapping')
                    continue
                missing = sorted(required - set(article))
                if missing:
                    errors.append(f'{article.get("id", f"article {i}")} missing fields: {", ".join(missing)}')

    for rel in ['constitution.md', 'index.json', 'logs/amendments', 'logs/judgments', 'logs/recommendations']:
        if not (home / rel).exists():
            errors.append(f'missing {rel}')
    index_path = home / 'index.json'
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding='utf-8'))
            if not isinstance(index, dict):
                errors.append('index.json must contain a mapping')
            else:
                for key in ['judgments', 'amendments']:
                    if key not in index:
                        errors.append(f'index.json missing {key}')
                    elif not isinstance(index[key], dict):
                        errors.append(f'index.json {key} must be a mapping')
        except json.JSONDecodeError as exc:
            errors.append(f'index.json is invalid JSON: {exc}')

    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        return 1

    print(f'OK: {home}')
    print(f'version: {data.get("constitution_version")}')
    print(f'articles: {len(data.get("articles", []))}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
