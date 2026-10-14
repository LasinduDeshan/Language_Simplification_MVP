"""
Stage 29 Cross-Layer Grapheme Cluster Parity Verification
Verifies strict count equivalence between Backend (unicodedata UAX #29)
and Frontend (Intl.Segmenter + pinned fallback) across all governed fixtures.
"""

import json
import subprocess
from pathlib import Path
from app.localization.unicode_guards import count_grapheme_clusters

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def test_cross_layer_grapheme_parity():
    # 1. Collect all governed text samples from fixtures and probes
    fixtures_dir = PROJECT_ROOT / "data" / "sinhala_foundation" / "fixtures"
    unicode_cases_file = fixtures_dir / "unicode_round_trip_cases.json"
    mixed_cases_file = fixtures_dir / "mixed_language_cases.json"

    with open(unicode_cases_file, "r", encoding="utf-8") as f:
        unicode_cases = json.load(f)
    with open(mixed_cases_file, "r", encoding="utf-8") as f:
        mixed_cases = json.load(f)

    samples = [c["input_text"] for c in unicode_cases] + [c["input_text"] for c in mixed_cases]
    # Add canonical probes
    samples.extend([
        "ශ්‍රී ලංකා ප්‍රජාතාන්ත්‍රික සමාජවාදී ජනරජය",
        "Grade 1: කියවීම",
        "අම්මා"
    ])

    # 2. Compute backend grapheme counts
    backend_counts = {text: count_grapheme_clusters(text) for text in samples}

    # 3. Compute frontend grapheme counts via Node.js
    node_script = """
    import { countGraphemes } from './src/i18n/graphemeSegmenter.js';
    import readline from 'readline';

    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    let input = '';
    rl.on('line', line => { input += line; });
    rl.on('close', () => {
        const samples = JSON.parse(input);
        const results = {};
        for (const s of samples) {
            results[s] = {
                native: countGraphemes(s, 'si-LK', false),
                fallback: countGraphemes(s, 'si-LK', true)
            };
        }
        console.log(JSON.stringify(results));
    });
    """

    frontend_dir = PROJECT_ROOT / "frontend"
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        input=json.dumps(samples),
        capture_output=True,
        text=True,
        cwd=str(frontend_dir),
        encoding="utf-8"
    )
    assert proc.returncode == 0, f"Node script failed: {proc.stderr}"
    frontend_results = json.loads(proc.stdout)

    # 4. Verify Parity
    mismatches = []
    for text in samples:
        b_count = backend_counts[text]
        f_native = frontend_results[text]["native"]
        f_fallback = frontend_results[text]["fallback"]

        # Ensure frontend native and fallback agree
        assert f_native == f_fallback, f"Frontend native/fallback mismatch for '{text}': {f_native} vs {f_fallback}"

        # Ensure frontend and backend agree
        if b_count != f_native:
            mismatches.append({
                "text": text,
                "backend": b_count,
                "frontend": f_native
            })

    assert len(mismatches) == 0, f"Cross-layer grapheme count mismatches found: {mismatches}"
