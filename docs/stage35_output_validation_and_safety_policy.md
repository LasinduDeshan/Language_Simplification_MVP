# Stage 35 Output Validation and Safety Policy

## 1. Guard Rules & Dispositions
- Unicode integrity: Zero introduced `U+FFFD`. Failure -> `REJECTED_INVALID_UNICODE_OR_SCRIPT`.
- Protected spans: Zero tolerance for corruption of sealed spans. Failure -> `REJECTED_PROTECTED_SPAN_CHANGE`.
- Heuristic safety & hallucination: Triggers `REVIEW_REQUIRED_POTENTIAL_*`.
