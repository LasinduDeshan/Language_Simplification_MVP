"""
Deduplication and Transitive Split Grouping Engine for Stage 31.
Implements exact hashing, token-shingle Jaccard near-duplicate detection,
multi-source duplicate provenance aggregation, and transitive connected component clustering.
"""

import collections
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

EXPORT_POLICY_PRECEDENCE = [
    "BLOCKED_PROPRIETARY",
    "BLOCKED_REVIEW_REQUIRED",
    "METADATA_CATALOGUE_ONLY",
    "PROTECTED_INTERNAL_ONLY",
    "PUBLIC_PERMITTED_CC_BY_SA",
    "PUBLIC_PERMITTED_CC_BY",
]

def resolve_most_restrictive_export_policy(policies: List[str]) -> str:
    """Returns the most restrictive export policy among the given list."""
    for p in EXPORT_POLICY_PRECEDENCE:
        if p in policies:
            return p
    return "PROTECTED_INTERNAL_ONLY"

def get_token_shingles(text: str, n: int = 5, shingle_type: str = "char") -> Set[str]:
    """Extracts character n-grams or token n-grams for Jaccard similarity calculation."""
    if shingle_type == "char":
        cleaned = re.sub(r'\s+', '', text)
        if len(cleaned) < n:
            return {cleaned}
        return {cleaned[i:i+n] for i in range(len(cleaned) - n + 1)}
    else:
        tokens = text.split()
        if len(tokens) < n:
            return {" ".join(tokens)}
        return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def compute_jaccard_similarity(shingles_a: Set[str], shingles_b: Set[str]) -> float:
    if not shingles_a or not shingles_b:
        return 0.0
    intersection = len(shingles_a.intersection(shingles_b))
    union = len(shingles_a.union(shingles_b))
    return float(intersection) / float(union) if union > 0 else 0.0

@dataclass
class NearDuplicateCandidate:
    record_a: str
    record_b: str
    similarity: float

class DeduplicationEngine:
    """Orchestrates exact and near-duplicate detection and transitive component formation."""

    def __init__(
        self,
        candidate_similarity_threshold: float = 0.80,
        confirmed_similarity_threshold: float = 0.90
    ):
        self.candidate_threshold = candidate_similarity_threshold
        self.confirmed_threshold = confirmed_similarity_threshold

    def find_exact_duplicates(self, record_text_map: Dict[str, str]) -> Dict[str, List[str]]:
        """Groups records with identical normalized text into duplicate clusters."""
        text_to_records: Dict[str, List[str]] = collections.defaultdict(list)
        for rec_id, text in record_text_map.items():
            text_to_records[text.strip()].append(rec_id)
        
        clusters: Dict[str, List[str]] = {}
        cluster_idx = 1
        for text, rec_ids in text_to_records.items():
            cluster_id = f"DUP-SI-{cluster_idx:06d}"
            clusters[cluster_id] = rec_ids
            cluster_idx += 1
        return clusters

    def find_near_duplicates(self, record_text_map: Dict[str, str]) -> List[NearDuplicateCandidate]:
        """Identifies candidate record pairs with token-shingle Jaccard similarity >= candidate_threshold."""
        shingles_map = {rec_id: get_token_shingles(text) for rec_id, text in record_text_map.items()}
        rec_ids = list(record_text_map.keys())
        candidates = []

        for i in range(len(rec_ids)):
            id_a = rec_ids[i]
            s_a = shingles_map[id_a]
            for j in range(i + 1, len(rec_ids)):
                id_b = rec_ids[j]
                s_b = shingles_map[id_b]
                sim = compute_jaccard_similarity(s_a, s_b)
                if sim >= self.candidate_threshold:
                    candidates.append(NearDuplicateCandidate(record_a=id_a, record_b=id_b, similarity=sim))
        return candidates

    def build_transitive_split_groups(
        self,
        all_record_ids: List[str],
        doc_group_map: Dict[str, str],
        exact_clusters: Dict[str, List[str]],
        confirmed_near_dups: List[Tuple[str, str]],
        dev_records: Set[str]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Computes transitive connected components across:
          - Same document_group_id
          - Same exact duplicate cluster
          - Confirmed near-duplicate edges
        Returns:
          (record_to_split_group, split_group_component_type)
        where split_group_component_type is TRAIN_ONLY_DEVELOPMENT_COMPONENT if any record in the group is a dev record.
        """
        # Graph adjacency
        adj: Dict[str, Set[str]] = collections.defaultdict(set)
        for rid in all_record_ids:
            adj[rid] = set()

        # 1. Document group edges
        doc_groups: Dict[str, List[str]] = collections.defaultdict(list)
        for rid, grp in doc_group_map.items():
            doc_groups[grp].append(rid)
        for grp, members in doc_groups.items():
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    adj[members[i]].add(members[j])
                    adj[members[j]].add(members[i])

        # 2. Exact duplicate edges
        for cluster_id, members in exact_clusters.items():
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    adj[members[i]].add(members[j])
                    adj[members[j]].add(members[i])

        # 3. Confirmed near-duplicate edges
        for a, b in confirmed_near_dups:
            adj[a].add(b)
            adj[b].add(a)

        # BFS connected components
        visited: Set[str] = set()
        record_to_split_group: Dict[str, str] = {}
        split_group_types: Dict[str, str] = {}
        component_idx = 1

        for rid in sorted(all_record_ids):
            if rid not in visited:
                split_group_id = f"SPLIT-GRP-SI-{component_idx:06d}"
                queue = [rid]
                visited.add(rid)
                component_members = []

                while queue:
                    curr = queue.pop(0)
                    component_members.append(curr)
                    record_to_split_group[curr] = split_group_id
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                # Invariant 18 & 19:
                # If ANY record in this component is in the dev pool, mark entire component as TRAIN_ONLY_DEVELOPMENT_COMPONENT
                has_dev = any(m in dev_records for m in component_members)
                if has_dev:
                    split_group_types[split_group_id] = "TRAIN_ONLY_DEVELOPMENT_COMPONENT"
                else:
                    split_group_types[split_group_id] = "UNTOUCHED_EVAL_ELIGIBLE_COMPONENT"

                component_idx += 1

        return record_to_split_group, split_group_types
