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


def count_files(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.glob(pattern) if item.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description='Inspect an agent constitution store without modifying it.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--articles', action='store_true', help='Print article id, rank, and title list.')
    args = parser.parse_args()

    home = resolve_home(args.home)
    result: dict[str, object] = {
        'home': str(home),
        'exists': home.exists(),
        'constitution_yaml': str(home / 'constitution.yaml'),
        'constitution_md': str(home / 'constitution.md'),
        'index_json': str(home / 'index.json'),
        'constitution_version': None,
        'article_count': 0,
        'judgment_log_count': count_files(home / 'logs' / 'judgments', '*'),
        'amendment_log_count': count_files(home / 'logs' / 'amendments', '*'),
        'recommendation_log_count': count_files(home / 'logs' / 'recommendations', '*'),
        'index_judgments': None,
        'index_amendments': None,
    }

    yaml_path = home / 'constitution.yaml'
    articles = []
    if yaml_path.exists() and yaml is not None:
        data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            result['constitution_version'] = data.get('constitution_version')
            articles = data.get('articles') or []
            result['article_count'] = len(articles) if isinstance(articles, list) else 0
    elif yaml_path.exists():
        result['constitution_yaml_note'] = 'PyYAML is not installed; skipped YAML parsing.'

    index_path = home / 'index.json'
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding='utf-8'))
        if isinstance(index, dict):
            judgments = index.get('judgments')
            amendments = index.get('amendments')
            result['index_judgments'] = len(judgments) if isinstance(judgments, (dict, list)) else None
            result['index_amendments'] = len(amendments) if isinstance(amendments, (dict, list)) else 0

    print(json.dumps(result, indent=2, sort_keys=True))
    if args.articles and isinstance(articles, list):
        for article in sorted(articles, key=lambda item: item.get('rank', 999999) if isinstance(item, dict) else 999999):
            if isinstance(article, dict):
                print(f"{article.get('id')}\t{article.get('rank')}\t{article.get('title')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
