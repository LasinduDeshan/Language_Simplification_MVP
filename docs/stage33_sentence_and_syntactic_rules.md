# Stage 33 — Sentence Splitting and Conservative Syntactic Rules

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sentence splitting, constrained subject recovery, discourse filler deletion, and non-local trace mapping  
**Governance Checkpoint:** Stage 33 Technical Draft  

---

## 1. Sentence Splitting Engine (`sentence_splitter.py`)

Sentence splitting decomposes compound sentences at allowlisted coordination markers to improve syntactical accessibility for young readers.

### Splitting Criteria
1. Split occurs at approved coordinating markers (`සහ`, `නමුත්`).
2. Both resulting clauses must satisfy minimum completeness (at least 3 tokens each).
3. The split boundary must not bisect any protected entity, quotation, or parenthetical span.
4. Punctuation is reconstructed deterministically (`.` followed by space).

### Constrained Subject Recovery
Splitting a sentence can leave the second clause without an overt subject.
- **Allowed:** Subject insertion is permitted **only** when the exact subject noun phrase is verbatim extracted from an unambiguous source span in clause 1 and mapped directly to it.
- **Prohibited:** Subject invention, pronominal guessing, or ungrounded referent creation.
- **Routing:** If the referent is ambiguous or competing candidates exist, the rule attempt is set to `terminal_status: "DEFERRED_MANUAL_REVIEW"` and routes to `MANUAL_REVIEW_REQUIRED`.

### Registered Splitting Rules

- **`SI-SNT-SPL-0001` (`සහ` splitting):**
  - Priority: 50
  - Evidence: `SI-LEX-000908`.
  - Mapping: `non_local`, `mapping_exact: false`.
- **`SI-SNT-SPL-0002` (`නමුත්` adversative splitting):**
  - Priority: 60
  - Evidence: `SI-SPLIT-MARKER-02`.
  - Mapping: `non_local`, `mapping_exact: false`.

---

## 2. Conservative Syntactic Simplification Engine (`syntactic_rules.py`)

Syntactic simplification rules perform deterministic restructuring or removal of redundant discourse particles without altering propositional meaning.

### Registered Syntactic Rules

- **`SI-SYN-CON-0001` (Discourse filler removal: `ඇත්තෙන්ම`):**
  - Priority: 70
  - Evidence: `SI-SYN-FILLER-01`.
  - Action: Removes sentence-initial or non-restrictive filler `ඇත්තෙන්ම`.
  - Mapping: `deleted`, `mapping_exact: false`.
