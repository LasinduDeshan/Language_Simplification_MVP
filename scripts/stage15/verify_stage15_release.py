"""Verifies Stage 15 deliverables, reports, and creates SHA-256 integrity manifest."""
import os
import sys
import hashlib

TARGET_FILES = [
    os.path.join("docs", "stage15_quality_policy.md"),
    os.path.join("docs", "stage15_threshold_policy.md"),
    os.path.join("docs", "stage15_manual_review_policy.md"),
    os.path.join("docs", "stage15_llm_validation_policy.md"),
    os.path.join("docs", "stage15_rule_catalogue.csv"),
    os.path.join("data", "quality_reports", "stage15", "public", "stage15_quality_report.json"),
    os.path.join("data", "quality_reports", "stage15", "public", "stage15_quality_summary.csv"),
]


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manifest_lines = []

    print("==================================================================")
    print("STAGE 15 DELIVERABLE CHECKSUM VERIFICATION")
    print("==================================================================")

    for rel_path in TARGET_FILES:
        full_path = os.path.join(repo_root, rel_path)
        if os.path.exists(full_path):
            sha = compute_sha256(full_path)
            normalized_path = rel_path.replace("\\", "/")
            manifest_lines.append(f"{sha}  {normalized_path}")
            print(f"[OK] {sha[:16]}... {normalized_path}")
        else:
            print(f"[!] Warning: Missing expected file '{rel_path}'")

    manifest_path = os.path.join(repo_root, "docs", "stage15_manifest.sha256")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")

    print(f"\n[+] Wrote complete manifest to '{manifest_path}'.")
    print("==================================================================")


if __name__ == "__main__":
    main()
