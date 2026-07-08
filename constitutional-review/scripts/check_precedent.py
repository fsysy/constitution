#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path


def resolve_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    env_value = os.environ.get('AGENT_CONSTITUTION_HOME')
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path.home() / '.agent-constitution'


def normalize_text(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip().lower())


def sha256_text(value: str) -> str:
    return 'sha256:' + hashlib.sha256(value.encode('utf-8')).hexdigest()


def compute_fingerprint(source_type: str, source_ref: str, accused_action: str, article_ids: list[str], evidence_hash: str) -> str:
    payload = {
        'source_type': source_type,
        'source_ref': source_ref,
        'normalized_accused_action': normalize_text(accused_action),
        'article_ids': sorted(article_ids),
        'evidence_hash': evidence_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return sha256_text(encoded)


def load_index(home: Path) -> dict:
    index_path = home / 'index.json'
    if not index_path.exists():
        return {'judgments': {}, 'amendments': {}}
    return json.loads(index_path.read_text(encoding='utf-8'))


def find_judgment(judgments: object, fingerprint: str) -> object | None:
    if isinstance(judgments, dict):
        return judgments.get(fingerprint)
    if isinstance(judgments, list):
        for item in judgments:
            if isinstance(item, dict) and item.get('fingerprint') == fingerprint:
                return item
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description='Check whether an identical constitutional review case has already been judged.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--fingerprint', help='Existing case fingerprint to look up directly. Useful for legacy indexes.')
    parser.add_argument('--source-type', help='Evidence source type, such as git_commit, diff, document, or conversation.')
    parser.add_argument('--source-ref', help='Evidence source reference, such as commit hash, file path, or document id.')
    parser.add_argument('--accused-action', help='Normalized allegation or accused action.')
    parser.add_argument('--article', action='append', dest='articles', help='Article ID. Repeat for multiple articles.')
    parser.add_argument('--evidence-summary', default='', help='Evidence summary used to derive evidence hash when --evidence-hash is omitted.')
    parser.add_argument('--evidence-hash', help='Precomputed evidence hash, usually sha256:...')
    args = parser.parse_args()

    home = resolve_home(args.home)
    if args.fingerprint:
        fingerprint = args.fingerprint
    else:
        missing = [name for name, value in [
            ('--source-type', args.source_type),
            ('--source-ref', args.source_ref),
            ('--accused-action', args.accused_action),
            ('--article', args.articles),
        ] if not value]
        if missing:
            parser.error(f'argument(s) required unless --fingerprint is provided: {", ".join(missing)}')
        evidence_hash = args.evidence_hash or sha256_text(args.evidence_summary)
        fingerprint = compute_fingerprint(args.source_type, args.source_ref, args.accused_action, args.articles, evidence_hash)
    index = load_index(home)
    judgments = index.get('judgments', {})
    match = find_judgment(judgments, fingerprint)

    result = {
        'fingerprint': fingerprint,
        'already_judged': bool(match),
        'case_id': None,
        'judgment_path': None,
    }
    if isinstance(match, str):
        result['case_id'] = match
        result['judgment_path'] = str(home / 'logs' / 'judgments' / f'{match}.json')
    elif isinstance(match, dict):
        result['case_id'] = match.get('case_id')
        path = match.get('path') or match.get('log_path')
        if path:
            result['judgment_path'] = str(home / path)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not match else 2


if __name__ == '__main__':
    raise SystemExit(main())
