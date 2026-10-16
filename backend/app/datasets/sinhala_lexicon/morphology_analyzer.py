"""
Conservative Rule-Based Morphology Analyzer for Stage 32 Sinhala Lexicon.
Generates candidate lemma and inflectional family hypotheses with explicit
confidence scoring and rule versioning. Does NOT claim human linguistic truth.
"""

from typing import List, Optional, Tuple
from app.datasets.sinhala_lexicon.schemas import MorphologyHypothesis
from app.datasets.sinhala_lexicon.enums import LemmaMethod

class MorphologyAnalyzer:
    """Proposes conservative inflectional and derivational hypotheses for Sinhala candidates."""

    RULE_VERSION = "1.0.0"

    def __init__(self):
        # Common regular Sinhala nominal inflection suffixes and case markers
        self.plural_suffixes = [
            ("වල්", "PLURAL_SUFFIX_WAL", 0.85),
            ("වල", "PLURAL_LOCATIVE_SUFFIX_WALA", 0.85),
            ("වරු", "PLURAL_SUFFIX_WARU", 0.80),
            ("වරුන්", "PLURAL_SUFFIX_WARUN", 0.85),
            ("යන්", "PLURAL_SUFFIX_YAN", 0.80),
            ("යින්", "PLURAL_SUFFIX_YIN", 0.80),
            ("ඉන්", "PLURAL_SUFFIX_IN", 0.75),
            ("න්", "PLURAL_SUFFIX_N", 0.70)
        ]

        self.case_suffixes = [
            ("ගෙන්", "CASE_ABLATIVE_GEN", 0.85),
            ("ගෙ", "CASE_GENITIVE_GE", 0.80),
            ("ට", "CASE_DATIV_TA", 0.75),
            ("ද", "PARTICLE_QUESTION_DA", 0.70),
            ("ත්", "PARTICLE_CONJUNCTION_TH", 0.70),
            ("ම", "PARTICLE_EMPHASIS_MA", 0.70)
        ]

    def analyze_candidate(
        self,
        surface: str
    ) -> Tuple[Optional[str], LemmaMethod, float, List[MorphologyHypothesis]]:
        """
        Analyzes surface form against conservative rule sets.
        Returns:
            (candidate_lemma, lemma_method, confidence, hypotheses_list)
        """
        hypotheses: List[MorphologyHypothesis] = []

        # 1. Check plural suffixes
        for suffix, rule_id, conf in self.plural_suffixes:
            if surface.endswith(suffix) and len(surface) > len(suffix) + 1:
                stem = surface[:-len(suffix)]
                # Add hypothesis
                hyp = MorphologyHypothesis(
                    rule_id=rule_id,
                    rule_version=self.RULE_VERSION,
                    base_form=stem,
                    inflected_form=surface,
                    confidence=conf,
                    linguistic_note="Illustrative rule-based morphology hypothesis; not expert-validated linguistic evidence."
                )
                hypotheses.append(hyp)

        # 2. Check case and clitic markers
        for suffix, rule_id, conf in self.case_suffixes:
            if surface.endswith(suffix) and len(surface) > len(suffix) + 1:
                stem = surface[:-len(suffix)]
                hyp = MorphologyHypothesis(
                    rule_id=rule_id,
                    rule_version=self.RULE_VERSION,
                    base_form=stem,
                    inflected_form=surface,
                    confidence=conf,
                    linguistic_note="Illustrative rule-based morphology hypothesis; not expert-validated linguistic evidence."
                )
                hypotheses.append(hyp)

        if not hypotheses:
            # Identity canonical
            return surface, LemmaMethod.IDENTITY_CANONICAL, 1.0, []

        # Conservative selection: pick highest confidence hypothesis if unambiguous
        sorted_hyp = sorted(hypotheses, key=lambda h: h.confidence, reverse=True)
        top_hyp = sorted_hyp[0]

        # If multiple hypotheses share the highest confidence, route with lower confidence
        top_ties = [h for h in sorted_hyp if h.confidence == top_hyp.confidence]
        if len(top_ties) > 1:
            # Ambiguous: retain top base form but lower confidence to 0.50
            return top_hyp.base_form, LemmaMethod.RULE_BASED_INFLECTION_V1, 0.50, hypotheses

        return top_hyp.base_form, LemmaMethod.RULE_BASED_INFLECTION_V1, top_hyp.confidence, hypotheses
