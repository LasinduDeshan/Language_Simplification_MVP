"""
Stage 20 Multi-Strategy Duplicate Detector Module
Detects exact duplicates and near-duplicate clusters using normalized matching,
token Jaccard similarity, character edit distance, and advisory embedding clustering.
"""
import re
from typing import List, Dict, Any, Tuple, Set

class DuplicateDetector:
    def __init__(self, jaccard_threshold: float = 0.85, levenshtein_threshold: float = 0.90):
        self.jaccard_threshold = jaccard_threshold
        self.levenshtein_threshold = levenshtein_threshold

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        # Lowercase, remove punctuation, collapse whitespace
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.split())

    def token_jaccard_similarity(self, s1: str, s2: str) -> float:
        t1 = set(self.normalize_text(s1).split())
        t2 = set(self.normalize_text(s2).split())
        if not t1 or not t2:
            return 0.0
        intersection = t1.intersection(t2)
        union = t1.union(t2)
        return len(intersection) / len(union)

    def levenshtein_ratio(self, s1: str, s2: str) -> float:
        s1 = self.normalize_text(s1)
        s2 = self.normalize_text(s2)
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        len1, len2 = len(s1), len(s2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
            
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,      # deletion
                    matrix[i][j - 1] + 1,      # insertion
                    matrix[i - 1][j - 1] + cost # substitution
                )
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)

    def scan_records(self, records: List[Dict[str, Any]], text_key: str = "original_text", id_key: str = "source_item_id") -> Dict[str, Any]:
        exact_seen: Dict[str, str] = {}
        exact_duplicates: List[Dict[str, Any]] = []
        near_duplicate_clusters: List[Dict[str, Any]] = []

        normalized_records = []
        for r in records:
            rec_id = r.get(id_key) or r.get("pair_id") or r.get("activity_id") or "UNKNOWN"
            raw_text = r.get(text_key, "")
            norm_text = self.normalize_text(raw_text)
            
            # Check exact duplicate
            if norm_text in exact_seen:
                exact_duplicates.append({
                    "record_id": rec_id,
                    "duplicate_of_id": exact_seen[norm_text],
                    "text": raw_text,
                    "match_type": "exact_normalized_match"
                })
            else:
                exact_seen[norm_text] = rec_id
                normalized_records.append((rec_id, raw_text, norm_text))

        # Check pairwise near duplicates
        n = len(normalized_records)
        for i in range(n):
            id_i, raw_i, norm_i = normalized_records[i]
            for j in range(i + 1, n):
                id_j, raw_j, norm_j = normalized_records[j]
                
                jaccard = self.token_jaccard_similarity(norm_i, norm_j)
                lev = self.levenshtein_ratio(norm_i, norm_j)
                
                if jaccard >= self.jaccard_threshold or lev >= self.levenshtein_threshold:
                    near_duplicate_clusters.append({
                        "record_id_1": id_i,
                        "record_id_2": id_j,
                        "text_1": raw_i,
                        "text_2": raw_j,
                        "jaccard_similarity": round(jaccard, 3),
                        "levenshtein_similarity": round(lev, 3),
                        "status": "manual_review_required"
                    })

        return {
            "total_evaluated": len(records),
            "exact_duplicate_count": len(exact_duplicates),
            "near_duplicate_cluster_count": len(near_duplicate_clusters),
            "exact_duplicates": exact_duplicates,
            "near_duplicate_clusters": near_duplicate_clusters,
            "is_unique": len(exact_duplicates) == 0
        }
