# Stage 33 — Lexical and Phrase-Level Simplification Rules

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Lexical substitutions, phrase-level longest-match rules, morphology preservation, and rights bindings  
**Governance Checkpoint:** Stage 33 Technical Draft  

---

## 1. Lexical Substitution Engine (`lexical_rules.py`)

Lexical substitution operates on allowlisted single-word or lemma patterns. A lexical rule may propose a replacement only when:
1. The rule ID and version are explicitly registered with human technical authorship.
2. The target form is supported by Stage 31/32 evidence references.
3. The source occurrence does not overlap any protected span.
4. The source occurrence is not within the scope of a negation marker (e.g., `තවදුරටත් නැත` idiom must not be simplified).
5. Inflectional and morphological agreement is preserved.

### Registered Lexical Rules

- **`SI-LEX-SUB-0001` (`පිළිබඳව` → `ගැන`):**
  - Priority: 100
  - Evidence: `SI-LEX-000550` (canonical freq 25) vs `SI-LEX-000185` (canonical freq 11).
  - Traces: `one_to_one`, `mapping_exact: true`.
- **`SI-LEX-SUB-0002` (`තවදුරටත්` → `තවත්`):**
  - Priority: 90
  - Evidence: `SI-LEX-000326` (freq 25) vs `SI-LEX-000325` (freq 14).
  - Safety check: Blocked when immediately followed by a negation marker.
- **`SI-LEX-SUB-0003` (`නිරීක්ෂණය` → `බැලීම`):**
  - Priority: 80
  - Evidence: `SI-LEX-000427`.

---

## 2. Phrase-Level Substitution Engine (`phrase_rules.py`)

Phrase-level rules replace multi-token idioms or compound grammatical structures with allowlisted simpler expressions.

### Longest-Match-First Precedence
- Phrase rules are assigned higher default priority (e.g., 140–150) than lexical rules (80–100).
- If a phrase rule matches a multi-token sequence, it supersedes constituent single-word lexical rules.

### Registered Phrase Rules

- **`SI-PHR-SUB-0001` (`මේ හේතුවෙන්` → `මේ නිසා`):**
  - Priority: 150
  - Evidence: `SI-LEX-000675`, `000681`.
  - Mapping: `many_to_one`, `mapping_exact: true`.
- **`SI-PHR-SUB-0002` (`ක්‍රියාත්මක කරනු ලබයි` → `කරයි`):**
  - Priority: 140
  - Evidence: `SI-LEX-000164`, `000216`.
  - Mapping: `many_to_one`, `mapping_exact: true`.
