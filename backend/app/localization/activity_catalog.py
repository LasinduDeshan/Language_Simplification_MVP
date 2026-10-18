"""
Governed Activity Catalog & Localized Activity Mapper
Component: Demonstration UI / Component 1 activity presentation
Stage 36 UI Correction: Real Activity Sinhala Availability
"""
from typing import Dict, Any, Optional, List
from app.localization.enums import TargetDisclosureClass, TargetDisclosurePolicy

GOVERNED_ACTIVITY_CATALOG: Dict[str, Dict[str, Any]] = {
    "VOC-NAMING-001": {
        "template_id": "VOC-NAMING-001",
        "title": {
            "en": "Name the Animal",
            "si": "සත්වයා නම් කරන්න"
        },
        "instruction": {
            "en": "Look at this picture. What animal do you see?",
            "si": "මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?"
        },
        "support_versions": {
            "mild": {
                "en": "What animal is this?",
                "si": "මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?"
            },
            "moderate": {
                "en": "Look at the animal. What is it?",
                "si": "මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?"
            },
            "strong": {
                "en": "Choose: cat or dog.",
                "si": "තෝරන්න: පූසා හෝ බල්ලා."
            },
            "strong_scaffold": {
                "en": "Choose: cat or dog.",
                "si": "තෝරන්න: පූසා හෝ බල්ලා."
            },
            "strong_decomposed_step": {
                "en": "Look at the picture closely. Choose the animal's name.",
                "si": "පින්තූරය හොඳින් බලන්න. සත්වයාගේ නම තෝරන්න."
            }
        },
        "options": [
            {"id": "cat", "label": {"en": "Cat", "si": "පූසා"}},
            {"id": "dog", "label": {"en": "Dog", "si": "බල්ලා"}},
            {"id": "rabbit", "label": {"en": "Rabbit", "si": "හාවා"}}
        ],
        "target_skill": "animal_naming",
        "target_id": "cat",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    },
    "VOC-NAMING-002": {
        "template_id": "VOC-NAMING-002",
        "title": {
            "en": "Name the Classroom Object",
            "si": "වස්තු හඳුනාගැනීම"
        },
        "instruction": {
            "en": "Show what we use to write with.",
            "si": "ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න."
        },
        "support_versions": {
            "mild": {
                "en": "Show what we use to write with.",
                "si": "ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න."
            },
            "moderate": {
                "en": "Which one is for writing?",
                "si": "ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න."
            },
            "strong": {
                "en": "Choose: pencil or book.",
                "si": "තෝරන්න: පැන්සල හෝ පොත."
            },
            "strong_scaffold": {
                "en": "Choose: pencil or book.",
                "si": "තෝරන්න: පැන්සල හෝ පොත."
            },
            "strong_decomposed_step": {
                "en": "Look at the two pictures. Choose what we use to write.",
                "si": "පින්තූර දෙක බලන්න. ලිවීමට භාවිත කරන දේ තෝරන්න."
            }
        },
        "options": [
            {"id": "pencil", "label": {"en": "Pencil", "si": "පැන්සල"}},
            {"id": "book", "label": {"en": "Book", "si": "පොත"}},
            {"id": "apple", "label": {"en": "Apple", "si": "ඇපල්"}}
        ],
        "target_skill": "object_identification",
        "target_id": "pencil",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    },
    "VOC-MATCH-001": {
        "template_id": "VOC-MATCH-001",
        "title": {
            "en": "Word-to-Picture Matching",
            "si": "පොත සෙවීම"
        },
        "instruction": {
            "en": "Find and touch the book.",
            "si": "පොතේ පින්තූරය සොයා තෝරන්න."
        },
        "support_versions": {
            "mild": {
                "en": "Find and touch the book.",
                "si": "පොතේ පින්තූරය සොයා තෝරන්න."
            },
            "moderate": {
                "en": "Touch the book.",
                "si": "පොතේ පින්තූරය සොයා තෝරන්න."
            },
            "strong": {
                "en": "Find the book.",
                "si": "පොත සොයන්න."
            },
            "strong_scaffold": {
                "en": "Find the book.",
                "si": "පොත සොයන්න."
            },
            "strong_decomposed_step": {
                "en": "Look at the two pictures. Choose the picture of the book.",
                "si": "පින්තූර දෙක බලන්න. පොතේ පින්තූරය තෝරන්න."
            }
        },
        "options": [
            {"id": "book", "label": {"en": "Book", "si": "පොත"}},
            {"id": "pencil", "label": {"en": "Pencil", "si": "පැන්සල"}},
            {"id": "ball", "label": {"en": "Ball", "si": "බෝලය"}}
        ],
        "target_skill": "picture_matching",
        "target_id": "book",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    },
    "VOC-CAT-001": {
        "template_id": "VOC-CAT-001",
        "title": {
            "en": "Category Sorting: Animals vs Food",
            "si": "ආහාර තේරීම"
        },
        "instruction": {
            "en": "Show what we can eat.",
            "si": "අපට ආහාරයට ගත හැකි දේ කුමක්දැයි පෙන්වන්න."
        },
        "support_versions": {
            "mild": {
                "en": "Show what we can eat.",
                "si": "අපට ආහාරයට ගත හැකි දේ කුමක්දැයි පෙන්වන්න."
            },
            "moderate": {
                "en": "Which one is food?",
                "si": "අපට ආහාරයට ගත හැකි දේ කුමක්දැයි පෙන්වන්න."
            },
            "strong": {
                "en": "Choose: apple or car.",
                "si": "තෝරන්න: ඇපල් හෝ මෝටර් රථය."
            },
            "strong_scaffold": {
                "en": "Choose: apple or car.",
                "si": "තෝරන්න: ඇපල් හෝ මෝටර් රථය."
            },
            "strong_decomposed_step": {
                "en": "Look at the two pictures. Choose what we can eat.",
                "si": "පින්තූර දෙක බලන්න. ආහාරයට ගත හැකි දේ තෝරන්න."
            }

        },
        "options": [
            {"id": "apple", "label": {"en": "Apple", "si": "ඇපල්"}},
            {"id": "car", "label": {"en": "Car", "si": "මෝටර් රථය"}},
            {"id": "book", "label": {"en": "Book", "si": "පොත"}}
        ],
        "target_skill": "category_recognition",
        "target_id": "apple",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    },
    "VOC-ODD-001": {
        "template_id": "VOC-ODD-001",
        "title": {
            "en": "Odd One Out",
            "si": "නොගැලපෙන රූපය සෙවීම"
        },
        "instruction": {
            "en": "Find the picture that does not belong.",
            "si": "මෙහි නොගැලපෙන රූපය තෝරන්න."
        },
        "support_versions": {
            "mild": {
                "en": "Find the picture that does not belong.",
                "si": "මෙහි නොගැලපෙන රූපය තෝරන්න."
            },
            "moderate": {
                "en": "Which picture is different?",
                "si": "මෙහි නොගැලපෙන රූපය තෝරන්න."
            },
            "strong": {
                "en": "Find the different one.",
                "si": "වෙනස් රූපය සොයන්න."
            },
            "strong_scaffold": {
                "en": "Find the different one.",
                "si": "වෙනස් රූපය සොයන්න."
            },
            "strong_decomposed_step": {
                "en": "Look at each picture. Choose the one that does not belong.",
                "si": "පින්තූර එකිනෙක බලන්න. නොගැලපෙන රූපය තෝරන්න."
            }

        },
        "options": [
            {"id": "apple", "label": {"en": "Apple", "si": "ඇපල්"}},
            {"id": "banana", "label": {"en": "Banana", "si": "කෙසෙල්"}},
            {"id": "car", "label": {"en": "Car", "si": "මෝටර් රථය"}}
        ],
        "target_skill": "odd_one_out",
        "target_id": "car",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    },
    "TASK-017": {
        "template_id": "TASK-017",
        "title": {
            "en": "Shape Match",
            "si": "හැඩතල ගැලපීම"
        },
        "instruction": {
            "en": "Touch the red circle.",
            "si": "රතු පාට වෘත්තය ස්පර්ශ කරන්න."
        },
        "support_versions": {
            "mild": {
                "en": "Touch the red circle.",
                "si": "රතු පාට වෘත්තය ස්පර්ශ කරන්න."
            },
            "moderate": {
                "en": "Find the red circle.",
                "si": "රතු පාට වෘත්තය ස්පර්ශ කරන්න."
            },
            "strong": {
                "en": "Touch: circle or square.",
                "si": "තෝරන්න: රතු වෘත්තය හෝ නිල් සමචතුරස්‍රය."
            },
            "strong_scaffold": {
                "en": "Touch: circle or square.",
                "si": "තෝරන්න: රතු වෘත්තය හෝ නිල් සමචතුරස්‍රය."
            },
            "strong_decomposed_step": {
                "en": "Look at the two shapes. Choose the red circle.",
                "si": "හැඩතල දෙක බලන්න. රතු පාට වෘත්තය තෝරන්න."
            }

        },
        "options": [
            {"id": "circle", "label": {"en": "Red Circle", "si": "රතු වෘත්තය"}},
            {"id": "square", "label": {"en": "Blue Square", "si": "නිල් සමචතුරස්‍රය"}},
            {"id": "triangle", "label": {"en": "Yellow Triangle", "si": "කහ ත්‍රිකෝණය"}}
        ],
        "target_skill": "shape_match",
        "target_id": "circle",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    }
}


# Aliases for cross-system consistency
GOVERNED_ACTIVITY_CATALOG["ACT-ANIMAL-001"] = GOVERNED_ACTIVITY_CATALOG["VOC-NAMING-001"]
GOVERNED_ACTIVITY_CATALOG["TASK-001"] = GOVERNED_ACTIVITY_CATALOG["VOC-NAMING-001"]
GOVERNED_ACTIVITY_CATALOG["ACT-OBJECT-001"] = GOVERNED_ACTIVITY_CATALOG["VOC-NAMING-002"]
GOVERNED_ACTIVITY_CATALOG["TASK-002"] = GOVERNED_ACTIVITY_CATALOG["VOC-NAMING-002"]
GOVERNED_ACTIVITY_CATALOG["ACT-BOOK-001"] = GOVERNED_ACTIVITY_CATALOG["VOC-MATCH-001"]
GOVERNED_ACTIVITY_CATALOG["TASK-003"] = GOVERNED_ACTIVITY_CATALOG["VOC-MATCH-001"]
GOVERNED_ACTIVITY_CATALOG["ACT-FOOD-001"] = GOVERNED_ACTIVITY_CATALOG["VOC-CAT-001"]
GOVERNED_ACTIVITY_CATALOG["TASK-006"] = GOVERNED_ACTIVITY_CATALOG["VOC-CAT-001"]
GOVERNED_ACTIVITY_CATALOG["ACT-ODD-001"] = GOVERNED_ACTIVITY_CATALOG["VOC-ODD-001"]
GOVERNED_ACTIVITY_CATALOG["TASK-007"] = GOVERNED_ACTIVITY_CATALOG["VOC-ODD-001"]
GOVERNED_ACTIVITY_CATALOG["ACT-SHAPE-001"] = GOVERNED_ACTIVITY_CATALOG["TASK-017"]


def get_governed_activity_localization(identifier: Optional[str]) -> Optional[Dict[str, Any]]:
    if not identifier:
        return None
    return GOVERNED_ACTIVITY_CATALOG.get(identifier)


def validate_activity_localization(task_or_dict: Any, requested_locale: str = "si") -> Dict[str, Any]:
    """
    Implements Section 4.3 availability reporting.
    Never silently copies English into a field labeled si.
    """
    norm_locale = "si" if requested_locale.lower().startswith("si") else "en"
    
    # Check if task already has Sinhala instruction
    has_si_instruction = False
    if hasattr(task_or_dict, "instruction_si") and getattr(task_or_dict, "instruction_si"):
        has_si_instruction = True
    elif isinstance(task_or_dict, dict) and task_or_dict.get("instruction_si"):
        has_si_instruction = True
    elif isinstance(task_or_dict, dict) and task_or_dict.get("instruction", {}).get("si"):
        has_si_instruction = True

    # Check via template catalog
    code = getattr(task_or_dict, "task_code", None) or (task_or_dict.get("task_code") if isinstance(task_or_dict, dict) else None)
    catalog_entry = get_governed_activity_localization(code)
    if catalog_entry and catalog_entry.get("instruction", {}).get("si"):
        has_si_instruction = True

    missing_fields = []
    if norm_locale == "si" and not has_si_instruction:
        missing_fields.append("instruction.si")

    return {
        "requested_locale": norm_locale,
        "content_available": len(missing_fields) == 0,
        "missing_localized_fields": missing_fields
    }


def enrich_task_localization(task: Any) -> Any:
    """Enriches a Task model or dictionary with canonical multilingual activity fields."""
    code = getattr(task, "task_code", None)
    cat = get_governed_activity_localization(code)
    task.activity_id = getattr(task, "id", None)
    task.template_id = code
    if cat:
        task.title_en = cat["title"]["en"]
        task.title_si = cat["title"]["si"]
        task.instruction_en = cat["instruction"]["en"]
        task.instruction_si = cat["instruction"]["si"]
        task.localized_title = cat["title"]
        task.localized_instruction = cat["instruction"]
        task.content_language_status = cat["content_language_status"]
    else:
        orig_title = getattr(task, "title", "")
        orig_inst = getattr(task, "child_friendly_instruction", None) or getattr(task, "original_instruction", "")
        task.title_en = orig_title
        task.title_si = None
        task.instruction_en = orig_inst
        task.instruction_si = None
        task.localized_title = {"en": orig_title}
        task.localized_instruction = {"en": orig_inst}
        task.content_language_status = {"en": "AVAILABLE", "si": "UNAVAILABLE"}
    return task


def enrich_attempt_localization(attempt: Any, task: Any, support_level: Optional[str] = None) -> Any:
    """Enriches an Attempt model or dictionary with canonical multilingual activity fields."""
    code = getattr(task, "task_code", None) if task else None
    cat = get_governed_activity_localization(code) if code else None
    attempt.activity_id = getattr(task, "id", None) if task else None
    attempt.template_id = code
    attempt.task_code = code

    presented_inst = getattr(attempt, "presented_instruction", None) or getattr(attempt, "instruction_shown", None) or ""
    level = support_level or getattr(attempt, "support_level", "moderate")

    strat = getattr(attempt, "adaptation_strategy", None)
    att_num = getattr(attempt, "attempt_number", 1)

    si_instruction = getattr(attempt, "presented_instruction_si", None)
    if not si_instruction and cat:
        sv = cat.get("support_versions", {})
        if strat and strat in sv:
            si_instruction = sv[strat].get("si")
        elif att_num == 3 and "strong_decomposed_step" in sv:
            si_instruction = sv["strong_decomposed_step"].get("si")
        elif att_num == 2 and "strong_scaffold" in sv:
            si_instruction = sv["strong_scaffold"].get("si")
        elif level in sv:
            si_instruction = sv[level].get("si")
        if not si_instruction and "instruction" in cat:
            si_instruction = cat["instruction"].get("si")

    if cat:
        attempt.title = cat["title"]
        attempt.instruction = {
            "en": presented_inst or cat["instruction"]["en"],
            "si": si_instruction
        } if si_instruction else {"en": presented_inst or cat["instruction"]["en"]}
        attempt.instruction_si = si_instruction
        attempt.presented_instruction_si = si_instruction
        attempt.options = cat.get("options")
        attempt.content_language_status = cat["content_language_status"]
        attempt.content_availability = validate_activity_localization(task, "si")
    else:
        orig_title = getattr(task, "title", "") if task else ""
        attempt.title = {"en": orig_title}
        attempt.instruction = {"en": presented_inst}
        attempt.instruction_si = None
        attempt.presented_instruction_si = None
        attempt.options = getattr(task, "options", None) if task else None
        attempt.content_language_status = {"en": "AVAILABLE", "si": "UNAVAILABLE"}
        attempt.content_availability = validate_activity_localization(task, "si") if task else {
            "requested_locale": "si",
            "content_available": False,
            "missing_localized_fields": ["instruction.si"]
        }

    # Extract simplification lineage and scoring flags if stored in snapshot
    snapshot = getattr(attempt, "automatic_analysis_snapshot", None)
    if isinstance(snapshot, dict):
        if "simplification_lineage" in snapshot:
            attempt.simplification_lineage = snapshot["simplification_lineage"]
        if "independent_performance_measure" in snapshot:
            attempt.independent_performance_measure = snapshot["independent_performance_measure"]
        if "score_interpretation" in snapshot:
            attempt.score_interpretation = snapshot["score_interpretation"]

    return attempt



def enrich_child_view_localization(view: Dict[str, Any], task: Any, attempt: Optional[Any] = None) -> Dict[str, Any]:
    """Enriches a child-safe view dictionary with canonical multilingual activity fields."""
    code = getattr(task, "task_code", None) if task else None
    cat = get_governed_activity_localization(code) if code else None
    level = getattr(attempt, "support_level", "moderate") if attempt else "moderate"
    presented_inst = view.get("presented_instruction", "")

    si_instruction = None
    if cat:
        if "support_versions" in cat and level in cat["support_versions"]:
            si_instruction = cat["support_versions"][level].get("si")
        if not si_instruction and "instruction" in cat:
            si_instruction = cat["instruction"].get("si")

        view["activity_id"] = getattr(task, "id", None)
        view["template_id"] = code
        view["task_code"] = code
        view["title"] = cat["title"]
        view["instruction"] = {
            "en": presented_inst or cat["instruction"]["en"],
            "si": si_instruction
        } if si_instruction else {"en": presented_inst or cat["instruction"]["en"]}
        view["instruction_si"] = si_instruction
        view["presented_instruction_si"] = si_instruction
        view["options"] = cat.get("options") or view.get("options")
        view["content_language_status"] = cat["content_language_status"]
        view["content_availability"] = validate_activity_localization(task, "si")
    else:
        view["activity_id"] = getattr(task, "id", None) if task else None
        view["template_id"] = code
        view["task_code"] = code
        view["title"] = {"en": getattr(task, "title", "")} if task else None
        view["instruction"] = {"en": presented_inst}
        view["instruction_si"] = None
        view["presented_instruction_si"] = None
        view["content_language_status"] = {"en": "AVAILABLE", "si": "UNAVAILABLE"}
        view["content_availability"] = validate_activity_localization(task, "si") if task else {
            "requested_locale": "si",
            "content_available": False,
            "missing_localized_fields": ["instruction.si"]
        }
    return view
