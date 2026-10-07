"""
B1: Lexical Substitution Baseline.
Substitutes complex vocabulary words with child-friendly alternatives using governed lexicons and age-gating.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import spacy
from app.baseline_simplification.schemas import BaselineMethodId

class LexicalSubstitutionBaseline:
    """Performs deterministic lexical substitutions governed by age-gating rules."""

    def __init__(
        self,
        lexicon_path: Optional[Path] = None,
        nlp: Optional[Any] = None,
        max_substitutions_per_sentence: int = 5,
    ):
        self.method_id = BaselineMethodId.B1
        self.method_version = "1.0.0"
        self.max_substitutions = max_substitutions_per_sentence
        
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")

        self.substitutions: Dict[str, Dict[str, Any]] = {}
        self._load_lexicon(lexicon_path)

    def _parse_age_bounds(self, entry: Dict[str, Any]) -> Tuple[int, int]:
        """Extracts minimum and maximum developmental age from lexicon entry fields."""
        if "minimum_age" in entry:
            min_a = int(entry["minimum_age"])
            max_a = int(entry.get("maximum_age", min_a + 2))
            return min_a, max_a

        if "age_band" in entry and entry["age_band"]:
            band_str = str(entry["age_band"])
            parts = re.findall(r"\d+", band_str)
            if len(parts) >= 2:
                return int(parts[0]), int(parts[1])
            elif len(parts) == 1:
                return int(parts[0]), int(parts[0]) + 2

        tier = entry.get("difficulty_tier", 2)
        if tier == 1:
            return 4, 6
        elif tier == 2:
            return 6, 8
        else:
            return 8, 12

    def _load_lexicon(self, lexicon_path: Optional[Path]) -> None:
        """Loads substitution dictionary from seed_vocabulary.json or provided path."""
        if lexicon_path is None:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            default_path = repo_root / "data" / "vocabulary_dictionary" / "seed_vocabulary.json"
            if default_path.exists():
                lexicon_path = default_path

        if lexicon_path and lexicon_path.exists():
            try:
                with open(lexicon_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        word = item.get("word", "").strip().lower()
                        alt = item.get("simple_alternative") or (item.get("simpler_alternatives", [None])[0])
                        if word and alt:
                            min_a, max_a = self._parse_age_bounds(item)
                            self.substitutions[word] = {
                                "simple_alternative": alt.strip(),
                                "minimum_age": min_a,
                                "maximum_age": max_a,
                                "difficulty": item.get("difficulty", "medium"),
                            }
            except Exception as e:
                print(f"Warning: Failed to load lexicon from {lexicon_path}: {e}")

    def _match_casing(self, orig_word: str, replacement: str) -> str:
        """Applies original word casing to replacement candidate."""
        if orig_word.isupper():
            return replacement.upper()
        if orig_word.istitle():
            return replacement.capitalize()
        return replacement.lower()

    def simplify(
        self,
        text: str,
        target_content_age: Optional[int] = 6,
        protected_tokens: Optional[Set[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Substitutes complex words exceeding target age with simpler alternatives."""
        if target_content_age is None:
            target_content_age = 6

        doc = self.nlp(text)
        rules_applied: List[Dict[str, Any]] = []
        operation_outcomes: List[Dict[str, Any]] = []
        
        # Protected tokens (entities, numbers, colors)
        prot_set = {t.lower() for t in (protected_tokens or set())}
        for ent in doc.ents:
            prot_set.add(ent.text.strip().lower())
        for token in doc:
            if token.pos_ == "PROPN":
                prot_set.add(token.text.strip().lower())

        modified_tokens = []
        sub_count = 0

        for token in doc:
            tok_text = token.text
            tok_lower = tok_text.lower()
            lemma_lower = token.lemma_.lower()

            # Candidate key in substitutions
            cand_key = tok_lower if tok_lower in self.substitutions else (lemma_lower if lemma_lower in self.substitutions else None)

            if cand_key and tok_lower not in prot_set and sub_count < self.max_substitutions:
                entry = self.substitutions[cand_key]
                min_age = entry["minimum_age"]
                alt = entry["simple_alternative"]

                # Age Gating: replace only if word difficulty > target_content_age
                if min_age > target_content_age or target_content_age <= 6:
                    replacement = self._match_casing(tok_text, alt)
                    modified_tokens.append(replacement + token.whitespace_)
                    sub_count += 1
                    rules_applied.append({
                        "rule_id": "LEX-02-AGE-TIER-GATE",
                        "step": len(rules_applied) + 1,
                        "details": {
                            "word": tok_text,
                            "replacement": replacement,
                            "target_age": target_content_age,
                            "source_min_age": min_age,
                        },
                    })
                    operation_outcomes.append({
                        "rule_id": "LEX-02-AGE-TIER-GATE",
                        "outcome": "applied",
                    })
                    continue

            modified_tokens.append(tok_text + token.whitespace_)

        result_text = "".join(modified_tokens).strip()
        return {
            "output_text": result_text,
            "rules_applied": rules_applied,
            "operation_outcomes": operation_outcomes,
            "fallback_used": False,
        }
