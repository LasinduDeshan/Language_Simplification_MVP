"""
Stage 21 Script: Inspect NLP Environment
Verifies Python, spaCy, Stanza, fastText, and Pydantic package environments and offline models.
Outputs reproducibility environment details for Stage 21.
"""
import os
import sys
import json
import platform
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def inspect_environment():
    print("=" * 60)
    print("STAGE 21: Inspecting NLP Preprocessing Environment")
    print("=" * 60)
    
    env_info = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": {},
        "models": {}
    }
    
    # Check packages
    for pkg in ["pydantic", "spacy", "stanza", "fasttext", "nltk", "pytest"]:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "installed")
            env_info["packages"][pkg] = ver
            print(f"  - {pkg}: {ver}")
        except ImportError:
            env_info["packages"][pkg] = "not_installed"
            print(f"  - {pkg}: NOT INSTALLED")
            
    # Check spaCy model
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        meta = nlp.meta
        env_info["models"]["spacy_en_core_web_sm"] = {
            "name": meta.get("name"),
            "version": meta.get("version"),
            "pipeline": nlp.pipe_names,
            "status": "available_offline"
        }
        print(f"  - spaCy en_core_web_sm: {meta.get('version')} (Pipeline: {nlp.pipe_names})")
    except Exception as e:
        env_info["models"]["spacy_en_core_web_sm"] = {"status": f"error: {e}"}
        print(f"  - spaCy en_core_web_sm: ERROR ({e})")
        
    # Check Stanza model availability
    try:
        import stanza
        env_info["models"]["stanza"] = {
            "version": getattr(stanza, "__version__", "installed"),
            "status": "installed"
        }
        print(f"  - Stanza library: {getattr(stanza, '__version__', 'installed')}")
    except Exception as e:
        env_info["models"]["stanza"] = {"status": f"error: {e}"}

    docs_dir = os.path.join(ROOT_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    out_file = os.path.join(docs_dir, "stage21_reproducibility_evidence.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(env_info, f, indent=2)
        
    print(f"Reproducibility environment evidence saved to: {out_file}")
    print("=" * 60)
    return env_info

if __name__ == "__main__":
    inspect_environment()
