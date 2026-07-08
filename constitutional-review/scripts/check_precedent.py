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


def main() -> int:
    parser = argparse.ArgumentParser(description='Check whether an identical constitutional review case has already been judged.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--source-type', required=True, help='Evidence source type, such as git_commit, diff, document, or conversation.')
    parser.add_argument('--source-ref', required=True, help='Evidence source reference, such as commit hash, file path, or document id.')
    parser.add_argument('--accused-action', required=True, help='Normalized allegation or accused action.')
    parser.add_argument('--article', action='append', required=True, dest='articles', help='Article ID. Repeat for multiple articles.')
    parser.add_argument('--evidence-summary', default='', help='Evidence summary used to derive evidence hash when --evidence-hash is omitted.')
    parser.add_argument('--evidence-hash', help='Precomputed evidence hash, usually sha256:...')
    args = parser.parse_args()

    home = resolve_home(args.home)
    evidence_hash = args.evidence_hash or sha256_text(args.evidence_summary)
    fingerprint = compute_fingerprint(args.source_type, args.source_ref, args.accused_action, args.articles, evidence_hash)
    index = load_index(home)
    judgments = index.get('judgments', {})
    match = judgments.get(fingerprint)

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
        if match.get('path'):
            result['judgment_path'] = str(home / match['path'])

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not match else 2


if __name__ == '__main__':
    raise SystemExit(main())
