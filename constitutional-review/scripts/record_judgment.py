#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path


VERDICTS = {'pardoned', 'guilty', 'not_guilty'}


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


def load_json(path: Path, fallback: dict) -> dict:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding='utf-8'))


def find_judgment(judgments: object, fingerprint: str) -> object | None:
    if isinstance(judgments, dict):
        return judgments.get(fingerprint)
    if isinstance(judgments, list):
        for item in judgments:
            if isinstance(item, dict) and item.get('fingerprint') == fingerprint:
                return item
    return None


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def next_case_id(judgments_dir: Path, today: dt.date) -> str:
    prefix = f'J-{today.isoformat()}-'
    highest = 0
    for path in judgments_dir.glob(f'{prefix}*.json'):
        suffix = path.stem.removeprefix(prefix)
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f'{prefix}{highest + 1:03d}'


def render_recommendation(case: dict, archive_path: Path, project_copy_path: str | None) -> str:
    articles = ', '.join(case['articles'])
    lines = [
        f"# Constitutional Remediation Recommendation: {case['case_id']}",
        '',
        f"- Verdict: `{case['verdict']}`",
        f"- Violated articles: {articles}",
        f"- Source: `{case['source']['type']}` `{case['source']['ref']}`",
        f"- Archive path: `{archive_path}`",
    ]
    if project_copy_path:
        lines.append(f"- Project copy path: `{project_copy_path}`")
    lines.extend([
        '',
        '## Evidence Summary',
        '',
        case['evidence_summary'],
        '',
        '## Prosecution Reason',
        '',
        case['prosecution_reason'],
        '',
        '## User Verdict Reason',
        '',
        case.get('verdict_reason') or 'No reason recorded.',
        '',
        '## Suggested Remediation',
        '',
        case.get('recommendation') or 'Review the violated articles and update the project only after separate user instruction.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Record a constitutional review judgment and update precedent index.')
    parser.add_argument('--home', help='Constitution home. Defaults to AGENT_CONSTITUTION_HOME or ~/.agent-constitution.')
    parser.add_argument('--source-type', required=True)
    parser.add_argument('--source-ref', required=True)
    parser.add_argument('--project-path', default='')
    parser.add_argument('--accused-action', required=True)
    parser.add_argument('--article', action='append', required=True, dest='articles')
    parser.add_argument('--evidence-summary', required=True)
    parser.add_argument('--evidence-hash')
    parser.add_argument('--prosecution-reason', required=True)
    parser.add_argument('--verdict', required=True, choices=sorted(VERDICTS))
    parser.add_argument('--verdict-reason', default='')
    parser.add_argument('--recommendation', default='')
    parser.add_argument('--project-copy-path', help='Optional project documentation path where the recommendation was copied.')
    parser.add_argument('--allow-duplicate', action='store_true', help='Record even when the fingerprint already exists.')
    args = parser.parse_args()

    home = resolve_home(args.home)
    judgments_dir = home / 'logs' / 'judgments'
    recommendations_dir = home / 'logs' / 'recommendations'
    index_path = home / 'index.json'
    judgments_dir.mkdir(parents=True, exist_ok=True)
    recommendations_dir.mkdir(parents=True, exist_ok=True)

    evidence_hash = args.evidence_hash or sha256_text(args.evidence_summary)
    fingerprint = compute_fingerprint(args.source_type, args.source_ref, args.accused_action, args.articles, evidence_hash)
    index = load_json(index_path, {'judgments': {}, 'amendments': {}})
    index.setdefault('judgments', {})
    index.setdefault('amendments', {})

    existing = find_judgment(index.get('judgments'), fingerprint)
    if existing and not args.allow_duplicate:
        print(json.dumps({'error': 'already_judged', 'fingerprint': fingerprint, 'existing': existing}, indent=2, sort_keys=True))
        return 2

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    case_id = next_case_id(judgments_dir, now.date())
    case = {
        'case_id': case_id,
        'fingerprint': fingerprint,
        'source': {'type': args.source_type, 'ref': args.source_ref},
        'project': {'path': args.project_path},
        'accused_action': normalize_text(args.accused_action),
        'articles': sorted(args.articles),
        'evidence_hash': evidence_hash,
        'evidence_summary': args.evidence_summary,
        'prosecution_reason': args.prosecution_reason,
        'verdict': args.verdict,
        'verdict_reason': args.verdict_reason,
        'recommendation': args.recommendation,
        'created_at': now.isoformat().replace('+00:00', 'Z'),
    }

    judgment_path = judgments_dir / f'{case_id}.json'
    write_json(judgment_path, case)
    index_entry = {
        'case_id': case_id,
        'fingerprint': fingerprint,
        'article_ids': sorted(args.articles),
        'project_path': args.project_path,
        'verdict': args.verdict,
        'path': str(judgment_path.relative_to(home)),
        'log_path': str(judgment_path.relative_to(home)),
        'created_at': case['created_at'],
    }

    recommendation_path = None
    if args.verdict == 'guilty':
        recommendation_path = recommendations_dir / f'{case_id}.md'
        recommendation_path.write_text(render_recommendation(case, recommendation_path, args.project_copy_path), encoding='utf-8')
        index_entry['recommendation_path'] = str(recommendation_path.relative_to(home))

    if isinstance(index.get('judgments'), list):
        index['judgments'].append(index_entry)
    elif isinstance(index.get('judgments'), dict):
        index['judgments'][fingerprint] = index_entry
    else:
        index['judgments'] = {fingerprint: index_entry}

    write_json(index_path, index)
    print(json.dumps({
        'case_id': case_id,
        'fingerprint': fingerprint,
        'judgment_path': str(judgment_path),
        'recommendation_path': str(recommendation_path) if recommendation_path else None,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
