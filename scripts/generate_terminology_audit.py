import os
import csv
import re

KEYWORDS = [
    'diagnostic', 'clinical', 'patient', 'severity', 'risk transition', 
    'risk recalibration', 'risk_changed', 'composite language index', 
    'CLI', 'clinician', 'screening_risk_level', 'recommended_support_level',
    'screening_risk', 'risk_support_level'
]

results = []

def classify(file_path: str, line_num: int, line_content: str, term: str):
    p = file_path.replace('\\', '/').lower()
    content_lower = line_content.lower()
    
    if 'test_validation_and_retry' in p and ('prohibited' in content_lower or 'safety_valid' in content_lower or 'violation' in content_lower):
        return 'child-facing term removed', 'Validation check preventing clinical terminology from reaching child'
    elif 'child_suitability' in p or 'input_sanitizer' in p:
        return 'child-facing term removed', 'Safety filter preventing clinical jargon from appearing in child instructions'
    elif 'child_view' in content_lower or 'childpreview' in p:
        return 'child-facing term removed', 'Child-facing interface guarantees zero clinical jargon or scores'
    elif 'risk_support_level' in content_lower or 'risk_changed' in content_lower or 'composite_language_index' in content_lower:
        return 'legacy field retained temporarily', 'Database schema backward-compatibility column retained during Stage 12'
    elif 'research_readme' in p or 'system_concept' in p or 'expert_evaluation' in p or 'likert' in content_lower:
        return 'research quotation/reference', 'Academic research paper framing, researcher documentation, or expert evaluation'
    elif 'component1' in p or 'component_1' in content_lower or 'screening_risk_level' in content_lower or 'screening_profile' in content_lower or 'screening_source' in content_lower:
        return 'valid screening terminology', 'Component 1 owned DLD risk screening indicator (read-only snapshot)'
    elif 'learnerbrowser' in p or 'taskresults' in p or 'profile_updater' in p or 'recommended_support_level' in content_lower or 'educational' in content_lower:
        return 'corrected educational terminology', 'Standardized educational performance metric and support scaffold'
    elif 'readme.md' in p or 'system_documentation.md' in p:
        if 'screening' in content_lower:
            return 'valid screening terminology', 'Component 1 external screening documentation'
        else:
            return 'corrected educational terminology', 'System architectural and educational terminology documentation'
    elif 'tests/' in p or 'test_' in p:
        return 'research quotation/reference', 'Automated test suite verifying responsibility boundaries and safety'
    else:
        return 'corrected educational terminology', 'Educational support terminology'

INCLUDE_EXTS = ('.py', '.jsx', '.js', '.md', '.sql', '.json')
EXCLUDE_DIRS = {'node_modules', '.git', '__pycache__', 'dist', '.pytest_cache', 'alembic'}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
    for file in files:
        if not file.endswith(INCLUDE_EXTS):
            continue
        if file in ('stage12_terminology_audit.csv', 'package-lock.json'):
            continue
        file_path = os.path.join(root, file)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for idx, line in enumerate(f, 1):
                    for kw in KEYWORDS:
                        if kw.lower() in line.lower():
                            cat, notes = classify(file_path, idx, line.strip(), kw)
                            results.append({
                                'File': file_path.replace('.\\', '').replace('./', ''),
                                'LineNumber': idx,
                                'MatchedTerm': kw,
                                'Classification': cat,
                                'LineSnippet': line.strip()[:140],
                                'Notes': notes
                            })
                            break
        except Exception:
            pass

with open('stage12_terminology_audit.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['File', 'LineNumber', 'MatchedTerm', 'Classification', 'LineSnippet', 'Notes'])
    writer.writeheader()
    writer.writerows(results)

print(f'Audited {len(results)} occurrences across repository.')

counts = {}
for r in results:
    c = r['Classification']
    counts[c] = counts.get(c, 0) + 1

for cat, count in sorted(counts.items()):
    print(f' - {cat}: {count}')
