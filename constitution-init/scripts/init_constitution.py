#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def resolve_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    env_value = os.environ.get('AGENT_CONSTITUTION_HOME')
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path.home() / '.agent-constitution'


def render_markdown(yaml_text: str) -> str:
    lines = ['# Agent Constitution', '', 'Canonical source: `constitution.yaml`', '']
    version = 'unknown'
    articles: list[tuple[str, str, str]] = []
    current_id = current_title = current_rank = None
    for raw in yaml_text.splitlines():
        line = raw.strip()
        if line.startswith('constitution_version:'):
            version = line.split(':', 1)[1].strip().strip("'")
        elif line.startswith('- id:'):
            current_id = line.split(':', 1)[1].strip()
            current_title = None
            current_rank = None
        elif line.startswith('rank:') and current_id:
            current_rank = line.split(':', 1)[1].strip()
        elif line.startswith('title:') and current_id:
            current_title = line.split(':', 1)[1].strip().strip('"')
            if current_rank:
                articles.append((current_id, current_rank, current_title))
                current_id = current_title = current_rank = None
    lines.extend([f'Constitution version: `{version}`', ''])
    for article_id, rank, title in articles:
        lines.extend([f'## {article_id}. {title}', '', f'Rank: {rank}', '', '_See constitution.yaml for full article text._', ''])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Initialize a private agent constitution store.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--force', action='store_true', help='Overwrite constitution.yaml and constitution.md if they exist.')
    args = parser.parse_args()

    home = resolve_home(args.home)
    skill_dir = Path(__file__).resolve().parents[1]
    starter = skill_dir / 'assets' / 'starter-constitution.yaml'
    yaml_text = starter.read_text(encoding='utf-8')

    home.mkdir(parents=True, exist_ok=True)
    for subdir in ['logs/amendments', 'logs/judgments', 'logs/recommendations']:
        (home / subdir).mkdir(parents=True, exist_ok=True)

    yaml_path = home / 'constitution.yaml'
    md_path = home / 'constitution.md'
    index_path = home / 'index.json'

    if yaml_path.exists() and not args.force:
        print(f'skip existing: {yaml_path}')
    else:
        yaml_path.write_text(yaml_text, encoding='utf-8')
        print(f'wrote: {yaml_path}')

    if md_path.exists() and not args.force:
        print(f'skip existing: {md_path}')
    else:
        md_path.write_text(render_markdown(yaml_text), encoding='utf-8')
        print(f'wrote: {md_path}')

    if index_path.exists() and not args.force:
        print(f'skip existing: {index_path}')
    else:
        index_path.write_text(json.dumps({'judgments': {}, 'amendments': {}}, indent=2) + '\n', encoding='utf-8')
        print(f'wrote: {index_path}')

    print(f'constitution_home: {home}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
