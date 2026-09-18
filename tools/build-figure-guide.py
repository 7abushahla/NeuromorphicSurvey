#!/usr/bin/env python3
"""Resolve data/figure-guide.json against the route data, the surveyed papers and the
source registry into data/generated/figure-guide-view.json, the one object the route map
reads (inlined into index.html by build-site.py; never hand-edited).

    python3 tools/build-figure-guide.py            # write
    python3 tools/build-figure-guide.py --check    # compare without writing
    python3 tools/build-figure-guide.py --self-test
"""
import argparse, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data/generated/figure-guide-view.json'
TYPE_WORD = {
    'official_vendor_documentation': 'official documentation', 'official_manufacturer_documentation': 'official documentation',
    'official_sdk_documentation': 'official documentation', 'official_devkit_manual': 'official documentation',
    'official_repository': 'official repository', 'official_model_zoo': 'official documentation',
    'official_mapper_constraints': 'official documentation', 'official_release_note': 'official documentation',
    'official_measured_example': 'official example', 'peer_reviewed': 'peer-reviewed', 'preprint': 'preprint',
    'datasheet': 'datasheet', 'trade_press': 'trade press', 'thesis': 'thesis',
}


def registry_lookup(registry):
    by = {}
    for r in registry['sources']:
        by[r['id']] = r
        for a in r.get('aliases', []):
            by[a.split(':', 1)[-1]] = r
    return by


def resolve_source(sid, by):
    r = by.get(sid)
    if not r:
        return None
    return {'id': r['id'], 'title': r.get('title') or r['id'], 'year': r.get('year'),
            'url': r.get('url') or (f"https://doi.org/{r['doi']}" if r.get('doi') else None),
            'type': TYPE_WORD.get(r.get('source_type') or '', (r.get('source_type') or 'source').replace('_', ' '))}


def build_view(guide, index, papers, registry):
    by = registry_lookup(registry)
    chips = {c['id'] for L in guide['layers'] for row in L['rows'] for c in row['chips']}
    nodes = {}
    for n in index['nodes']:
        if n['id'] in chips:
            nodes[n['id']] = {'id': n['id'], 'name': n.get('name'), 'type': n.get('type'), 'layer': n.get('layer'),
                              'target_kind': (n.get('attributes') or {}).get('target_kind'), 'summary': n.get('summary')}
    missing = sorted(chips - set(nodes))
    if missing:
        raise SystemExit(f"figure-guide: chips without a node: {missing}")
    edges = []
    for e in index['routes']:
        if e['from'] in chips and e['to'] in chips:
            srcs = []
            for sid in e.get('source_ids') or []:
                r = resolve_source(sid, by)
                if r is None:
                    raise SystemExit(f"figure-guide: edge {e['id']} names unregistered source {sid!r}")
                if r['url'] and r['id'] not in {s['id'] for s in srcs}:
                    srcs.append(r)
            edges.append({'id': e['id'], 'from': e['from'], 'to': e['to'], 'route_state': e.get('route_state'),
                          'evidence_class': e.get('evidence_class') or e.get('evidence'), 'sources': srcs})
    paper_by = {p['id']: p for p in papers['papers']}
    out_papers = {}
    for t in guide['toolchains'].values():
        for p in t.get('papers', []):
            rec = paper_by.get(p['id'])
            if rec is None:
                raise SystemExit(f"figure-guide: paper {p['id']!r} is not an evidence record")
            url = rec.get('url')
            if not url:
                reg = by.get(p['id']) or by.get((rec.get('sources') or [None])[0])
                url = reg and (reg.get('url') or (f"https://doi.org/{reg['doi']}" if reg.get('doi') else None))
            out_papers[p['id']] = {'id': p['id'], 'title': rec.get('title'), 'authors': rec.get('authors'), 'year': rec.get('year'),
                                   'venue': rec.get('venue'), 'url': url, 'evidence': rec.get('evidence'),
                                   'target_hardware': rec.get('target_hardware'), 'target_kind': rec.get('target_kind')}
    view = dict(guide)
    view.update({'generated_by': 'tools/build-figure-guide.py',
                 'generated_from': ['data/figure-guide.json', 'data/generated/route-index.json', 'data/evidence-papers.json', 'data/source-registry.json'],
                 'nodes': nodes, 'edges': edges, 'papers': out_papers})
    return view


def render(view):
    return (json.dumps(view, indent=1, ensure_ascii=False, sort_keys=False) + '\n').encode('utf-8')


class SelfTests(unittest.TestCase):
    def guide(self):
        return {'schema_version': 1, 'slots': ['dev', 'hw'],
                'layers': [{'id': 'sw', 'rows': [{'label': 'Develop and train', 'slot': 'dev', 'chips': [{'id': 'fw', 'label': 'FW'}]}]},
                           {'id': 'hw', 'rows': [{'label': 'H', 'slot': 'hw', 'bucket': 'neuromorphic', 'chips': [{'id': 'chip', 'label': 'Chip'}]}]}],
                'toolchains': {'t': {'papers': [{'id': 'p1', 'via': {}}], 'targets': ['chip'], 'steps': {'dev': 'fw'}, 'can': {'dev': ['fw']}},
                               't2': {'papers': [], 'targets': ['chip'], 'steps': {'dev': ['fw', 'other']}, 'can': {'dev': ['fw', 'other']},
                                      'breakAt': 'other', 'after': ['chip']}},
                'applications': {}, 'notes': {}, 'unreached': {}, 'buckets': [], 'seams': {}, 'rails': {'left': [], 'right': []}, 'quick': []}

    def index(self):
        return {'nodes': [{'id': 'fw', 'name': 'FW', 'type': 'framework', 'layer': 'Develop & simulate', 'summary': 's'},
                          {'id': 'chip', 'name': 'Chip', 'type': 'hardware', 'layer': 'Hardware', 'attributes': {'target_kind': 'neuromorphic'}, 'summary': 'c'},
                          {'id': 'other', 'name': 'O', 'type': 'runtime', 'layer': 'Runtime'}],
                'routes': [{'id': 'fw-chip', 'from': 'fw', 'to': 'chip', 'route_state': 'physical', 'evidence_class': 'E1', 'source_ids': ['alias-doc', 'nourl']},
                           {'id': 'fw-other', 'from': 'fw', 'to': 'other', 'source_ids': []}]}

    def registry(self):
        return {'sources': [{'id': 'doc', 'title': 'Doc', 'year': 2024, 'url': 'https://x/doc', 'source_type': 'official_sdk_documentation', 'aliases': ['targets-sources.json:alias-doc']},
                            {'id': 'nourl', 'title': 'No URL', 'year': 2020, 'url': None, 'doi': None, 'source_type': 'peer_reviewed', 'aliases': []},
                            {'id': 'p1', 'title': 'P1', 'year': 2025, 'url': None, 'doi': '10.1/p1', 'source_type': 'preprint', 'aliases': []}]}

    def papers(self):
        return {'papers': [{'id': 'p1', 'title': 'P1', 'authors': 'A', 'year': 2025, 'venue': 'V', 'url': None, 'evidence': 'E1', 'target_hardware': 'Chip', 'target_kind': 'neuromorphic', 'sources': ['p1']}]}

    def test_nodes_are_only_chips(self):
        v = build_view(self.guide(), self.index(), self.papers(), self.registry())
        self.assertEqual(set(v['nodes']), {'fw', 'chip'})
        self.assertEqual(v['nodes']['chip']['target_kind'], 'neuromorphic')

    def test_edges_between_chips_with_sources_resolved_through_aliases_and_urls_required(self):
        v = build_view(self.guide(), self.index(), self.papers(), self.registry())
        self.assertEqual([e['id'] for e in v['edges']], ['fw-chip'])
        self.assertEqual(v['edges'][0]['sources'], [{'id': 'doc', 'title': 'Doc', 'year': 2024, 'url': 'https://x/doc', 'type': 'official documentation'}])

    def test_paper_url_falls_back_to_registry_doi(self):
        v = build_view(self.guide(), self.index(), self.papers(), self.registry())
        self.assertEqual(v['papers']['p1']['url'], 'https://doi.org/10.1/p1')

    def test_unregistered_edge_source_fails(self):
        idx = self.index(); idx['routes'][0]['source_ids'] = ['ghost']
        with self.assertRaises(SystemExit):
            build_view(self.guide(), idx, self.papers(), self.registry())

    def test_render_is_deterministic(self):
        a = render(build_view(self.guide(), self.index(), self.papers(), self.registry()))
        b = render(build_view(self.guide(), self.index(), self.papers(), self.registry()))
        self.assertEqual(a, b)

    def test_list_valued_step_survives_copy_unchanged(self):
        v = build_view(self.guide(), self.index(), self.papers(), self.registry())
        self.assertEqual(v['toolchains']['t2']['steps']['dev'], ['fw', 'other'])
        self.assertEqual(v['toolchains']['t2']['after'], ['chip'])


def main():
    if '--self-test' in sys.argv:
        argv = [a for a in sys.argv if a != '--self-test']
        return 0 if unittest.main(argv=argv, exit=False).result.wasSuccessful() else 1
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); args = ap.parse_args()
    load = lambda p: json.loads((ROOT / p).read_text())
    view = build_view(load('data/figure-guide.json'), load('data/generated/route-index.json'),
                      load('data/evidence-papers.json'), load('data/source-registry.json'))
    data = render(view)
    if args.check:
        if not OUT.exists() or OUT.read_bytes() != data:
            print(f"figure guide view is stale: {OUT}"); return 1
        print(f"figure guide view is current: {OUT}"); return 0
    OUT.write_bytes(data)
    print(f"wrote {OUT} ({len(view['nodes'])} nodes, {len(view['edges'])} edges, {len(view['papers'])} papers)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
