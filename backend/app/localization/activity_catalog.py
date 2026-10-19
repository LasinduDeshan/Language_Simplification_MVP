"""
Governed Activity Catalog & Localized Activity Mapper
Component: Demonstration UI / Component 1 activity presentation
Stage 36 UI Correction: Real Activity Sinhala Availability
"""
from typing import Dict, Any, Optional, List
from app.localization.enums import TargetDisclosureClass, TargetDisclosurePolicy, GovernedTaskType, TaskType

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
    },
    "GRAM-WORD-001": {
        "template_id": "GRAM-WORD-001",
        "activity_id": "GRAM-WORD-001",
        "task_code": "GRAM-WORD-001",
        "activity_type": {
            "en": "Word Ordering",
            "si": "වචන පෙළගැස්වීම"
        },
        "title": {
            "en": "Word Ordering: S-V-O Sentence",
            "si": "කර්තෘ–ක්‍රියා–කර්ම වාක්‍යය පෙළගස්වන්න"
        },
        "description": {
            "en": "Arrange the words to create a correct sentence.",
            "si": "නිවැරදි වාක්‍යයක් සෑදීමට වචන පෙළගස්වන්න."
        },
        "instruction": {
            "en": "Put the words in the correct order.",
            "si": "වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න."
        },
        "support_versions": {
            "mild": {
                "en": "Put the words in the correct order.",
                "si": "වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න."
            },
            "moderate": {
                "en": "Arrange the words: The boy, likes, apples.",
                "si": "වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න: පිරිමි ළමයා, ඇපල්වලට, කැමතියි."
            },
            "strong": {
                "en": "Put the words in order: The boy likes apples.",
                "si": "වාක්‍යය හදන්න: පිරිමි ළමයා ඇපල්වලට කැමතියි."
            },
            "strong_scaffold": {
                "en": "Put the words in order to make a sentence.",
                "si": "වචන නිවැරදි අනුපිළිවෙළට තෝරන්න."
            },
            "strong_decomposed_step": {
                "en": "Choose the words one by one in the correct order.",
                "si": "වචන නිවැරදි අනුපිළිවෙළට එකින් එක තෝරන්න."
            }
        },
        "target_skill": {
            "code": "WORD_ORDER_SVO",
            "label": {
                "en": "S-V-O Word Order",
                "si": "කර්තෘ–ක්‍රියා–කර්ම වචන අනුපිළිවෙළ"
            }
        },
        "target_id": "TOKEN-001",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "tokens": [
            {
                "token_id": "TOKEN-001",
                "order": 1,
                "text": { "en": "The boy", "si": "පිරිමි ළමයා" }
            },
            {
                "token_id": "TOKEN-002",
                "order": 3,
                "text": { "en": "likes", "si": "කැමතියි" }
            },
            {
                "token_id": "TOKEN-003",
                "order": 2,
                "text": { "en": "apples", "si": "ඇපල්වලට" }
            }
        ],
        "options": [
            {"id": "TOKEN-001", "label": {"en": "The boy", "si": "පිරිමි ළමයා"}},
            {"id": "TOKEN-003", "label": {"en": "apples", "si": "ඇපල්වලට"}},
            {"id": "TOKEN-002", "label": {"en": "likes", "si": "කැමතියි"}}
        ],
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        }
    },
    "GRAM-SI-SUBPRED-001": {
        "template_id": "GRAM-SI-SUBPRED-001",
        "activity_id": "GRAM-SI-SUBPRED-001",
        "task_code": "GRAM-SI-SUBPRED-001",
        "content_version": 1,
        "task_type": "SUBJECT_PREDICATE_IDENTIFICATION",
        "activity_type": {
            "en": "Subject & Predicate Identification",
            "si": "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම"
        },
        "domain": "GRAMMAR",
        "category": "grammar",
        "target_id": "TOK-SUBJ",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "language": "si",
        "locale": "si-LK",
        "script": "Sinh",
        "minimum_age": 6,
        "maximum_age": 8,
        "target_age_min": 6,
        "target_age_max": 8,
        "base_difficulty": "medium",
        "delivery_modes": ["standard", "guided_playground"],
        "response_modes": ["multiple_choice", "manual_transcript"],
        "title": {
            "si": "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම",
            "en": "Identifying the Subject and Predicate"
        },
        "learning_objective": {
            "si": "සරල සිංහල වාක්‍යයක උක්තය සහ ආඛ්‍යාතය වෙන් කර හඳුනාගැනීම.",
            "en": "Identify and separate the subject and predicate in a simple Sinhala sentence."
        },
        "instruction": {
            "si": "වාක්‍යයේ උක්තය සහ ආඛ්‍යාතය හඳුනාගන්න.",
            "en": "Identify the subject and predicate in the sentence."
        },
        "description": {
            "si": "සිංහල වාක්‍යයක ප්‍රධාන කොටස් දෙකක් ලෙස උක්තය සහ ආඛ්‍යාතය හඳුනාගත හැක. උක්තය මඟින් වාක්‍යයේ කවුරුන් හෝ කුමක් ගැන කියන්නේද දක්වයි. ආඛ්‍යාතය මඟින් එම උක්තය ගැන කියන දෙය දක්වන අතර, සාමාන්‍යයෙන් එයට ක්‍රියා පදයක් ඇතුළත් වේ.",
            "en": "A Sinhala sentence can be examined as a subject and a predicate. The subject identifies whom or what the sentence is about. The predicate states something about the subject and normally contains the verb."
        },
        "short_explanation": {
            "si": "උක්තය කියන්නේ වාක්‍යය කවුරුන් හෝ කුමක් ගැනද කියන කොටසයි. ආඛ්‍යාතය කියන්නේ ඒ ගැන කියන දෙයයි.",
            "en": "The subject identifies whom or what the sentence is about. The predicate states what is said about it."
        },
        "agreement_note": {
            "si": "ලිඛිත සිංහලේදී උක්තය සහ ක්‍රියා පදය පුරුෂය, වචනය සහ ඇතැම් අවස්ථාවල ලිංගය අනුව ගැළපිය යුතුය.",
            "en": "In written Sinhala, the subject and verb must agree in person, number, and sometimes gender."
        },
        "support_versions": {
            "mild": {
                "si": "වාක්‍යය කවුරුන් හෝ කුමක් ගැනද සහ ඒ ගැන කියන දෙය කුමක්ද හඳුනාගන්න.",
                "en": "Identify whom or what the sentence is about and what is said about it."
            },
            "mild_support": {
                "si": "වාක්‍යය කවුරුන් හෝ කුමක් ගැනද සහ ඒ ගැන කියන දෙය කුමක්ද හඳුනාගන්න.",
                "en": "Identify whom or what the sentence is about and what is said about it."
            },
            "moderate": {
                "si": "පළමුව උක්තය තෝරන්න. ඉන්පසු ආඛ්‍යාතය තෝරන්න.",
                "en": "First select the subject. Then select the predicate."
            },
            "moderate_support": {
                "si": "පළමුව උක්තය තෝරන්න. ඉන්පසු ආඛ්‍යාතය තෝරන්න.",
                "en": "First select the subject. Then select the predicate."
            },
            "strong": {
                "si": "කවුද හෝ කුමක්ද? ඒ ගැන කියන්නේ කුමක්ද?",
                "en": "Who or what? What is said about it?"
            },
            "strong_scaffold": {
                "si": "කවුද හෝ කුමක්ද? ඒ ගැන කියන්නේ කුමක්ද?",
                "en": "Who or what? What is said about it?"
            },
            "strong_decomposed_step": {
                "si": "පළමුව “කවුද?” කියා සොයා එය තෝරන්න. දැන් ඒ අය කරන දෙය තෝරන්න.",
                "en": "First find who and select it. Now select what that person does."
            },
            "ORIGINAL_BASELINE": {
                "si": "වාක්‍යයේ උක්තය සහ ආඛ්‍යාතය හඳුනාගන්න.",
                "en": "Identify the subject and predicate in the sentence."
            },
            "MILD_SUPPORT": {
                "si": "වාක්‍යය කවුරුන් හෝ කුමක් ගැනද සහ ඒ ගැන කියන දෙය කුමක්ද හඳුනාගන්න.",
                "en": "Identify whom or what the sentence is about and what is said about it."
            },
            "MODERATE_SUPPORT": {
                "si": "පළමුව උක්තය තෝරන්න. ඉන්පසු ආඛ්‍යාතය තෝරන්න.",
                "en": "First select the subject. Then select the predicate."
            },
            "STRONG_SCAFFOLD": {
                "si": "කවුද හෝ කුමක්ද? ඒ ගැන කියන්නේ කුමක්ද?",
                "en": "Who or what? What is said about it?"
            },
            "STRONG_DECOMPOSED_STEP": {
                "si": "පළමුව “කවුද?” කියා සොයා එය තෝරන්න. දැන් ඒ අය කරන දෙය තෝරන්න.",
                "en": "First find who and select it. Now select what that person does."
            }
        },
        "feedback_copy": {
            "correct_subject": {
                "si": "හරි! “ළමයා” උක්තයයි.",
                "en": "Correct! “ළමයා” is the subject."
            },
            "correct_predicate": {
                "si": "හරි! “පොත කියවයි” ආඛ්‍යාතයයි.",
                "en": "Correct! “පොත කියවයි” is the predicate."
            },
            "incorrect_subject": {
                "si": "නැවත බලන්න. වාක්‍යය කවුරුන් ගැනද?",
                "en": "Try again. Whom is the sentence about?"
            },
            "incorrect_predicate": {
                "si": "නැවත බලන්න. උක්තය ගැන කියන්නේ කුමක්ද?",
                "en": "Try again. What does the sentence say about the subject?"
            },
            "completed": {
                "si": "හොඳයි! ඔබ උක්තය සහ ආඛ්‍යාතය හඳුනාගත්තා.",
                "en": "Well done! You identified the subject and predicate."
            }
        },
        "target_skill": {
            "code": "SUBJECT_PREDICATE_IDENTIFICATION",
            "label": {
                "si": "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම",
                "en": "Subject & Predicate Identification"
            }
        },
        "target_id": "ITEM-001",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "validation_status": "draft",
        "expert_validated": False,
        "research_eligible": False,
        "approved_for_child_delivery": False,
        "approved_for_unsupervised_child_delivery": False,
        "requires_expert_review": True,
        "content_language_status": {
            "en": "AVAILABLE",
            "si": "AVAILABLE"
        },
        "primary_example": {
            "item_id": "GRAM-SI-SUBPRED-001-I01",
            "sentence": "ළමයා පොත කියවයි.",
            "subject": "ළමයා",
            "predicate": "පොත කියවයි",
            "verb": "කියවයි",
            "subject_explanation": {
                "si": "වාක්‍යය කවුරුන් ගැනද කියයි",
                "en": "Tells whom the sentence is about"
            },
            "predicate_explanation": {
                "si": "ළමයා ගැන කියන දෙය",
                "en": "What is said about the subject"
            },
            "verb_explanation": {
                "si": "සිදු කරන ක්‍රියාව",
                "en": "The action being performed"
            }
        },
        "items": [
            {
                "item_id": "GRAM-SI-SUBPRED-001-I01",
                "sentence": "ළමයා පොත කියවයි.",
                "subject": "ළමයා",
                "predicate": "පොත කියවයි",
                "verb": "කියවයි"
            },
            {
                "item_id": "GRAM-SI-SUBPRED-001-I02",
                "sentence": "බල්ලා වේගයෙන් දුවයි.",
                "subject": "බල්ලා",
                "predicate": "වේගයෙන් දුවයි",
                "verb": "දුවයි"
            },
            {
                "item_id": "GRAM-SI-SUBPRED-001-I03",
                "sentence": "ගැහැනු ළමයා මලක් අඳියි.",
                "subject": "ගැහැනු ළමයා",
                "predicate": "මලක් අඳියි",
                "verb": "අඳියි"
            },
            {
                "item_id": "GRAM-SI-SUBPRED-001-I04",
                "sentence": "කුරුල්ලා ගස මත වාඩි වෙයි.",
                "subject": "කුරුල්ලා",
                "predicate": "ගස මත වාඩි වෙයි",
                "verb": "වාඩි වෙයි"
            },
            {
                "item_id": "GRAM-SI-SUBPRED-001-I05",
                "sentence": "අම්මා බත් පිසියි.",
                "subject": "අම්මා",
                "predicate": "බත් පිසියි",
                "verb": "පිසියි"
            }
        ],
        "tokens": [
            {
                "token_id": "TOK-SUBJ",
                "order": 1,
                "text": {"si": "ළමයා", "en": "The child"},
                "role": "subject",
                "role_label": {"si": "උක්තය", "en": "Subject"}
            },
            {
                "token_id": "TOK-PRED-1",
                "order": 2,
                "text": {"si": "පොත", "en": "the book"},
                "role": "predicate_object",
                "role_label": {"si": "ආඛ්‍යාත කොටස", "en": "Predicate Part"}
            },
            {
                "token_id": "TOK-PRED-2",
                "order": 3,
                "text": {"si": "කියවයි", "en": "reads"},
                "role": "verb",
                "role_label": {"si": "ක්‍රියා පදය (ආඛ්‍යාතය)", "en": "Verb (Predicate)"}
            }
        ],
        "options": [
            {
                "id": "OPT-SUBJ-001",
                "token_id": "TOK-SUBJ",
                "label": {"si": "ළමයා", "en": "The child"},
                "role": "subject"
            },
            {
                "id": "OPT-PRED-001",
                "token_id": "TOK-PRED-COMBINED",
                "label": {"si": "පොත කියවයි", "en": "reads the book"},
                "role": "predicate"
            }
        ]
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
GOVERNED_ACTIVITY_CATALOG["ACT-WORD-001"] = GOVERNED_ACTIVITY_CATALOG["GRAM-WORD-001"]
GOVERNED_ACTIVITY_CATALOG["ACT-SUBPRED-001"] = GOVERNED_ACTIVITY_CATALOG["GRAM-SI-SUBPRED-001"]


def is_uuid(val: Optional[str]) -> bool:
    if not val:
        return False
    import re
    return bool(re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", str(val).strip(), re.I))


def validate_token_structure(token: Any) -> bool:
    """Validates that a multilingual token contains token_id, order, and valid text map."""
    if not isinstance(token, dict):
        return False
    if "token_id" not in token or not isinstance(token["token_id"], str) or not token["token_id"].strip():
        return False
    if "order" not in token or not isinstance(token["order"], int):
        return False
    if "text" not in token or not isinstance(token["text"], dict):
        return False
    text_map = token["text"]
    if not any(isinstance(v, str) and v.strip() for v in text_map.values()):
        return False
    return True


def get_governed_activity_localization(identifier: Optional[str]) -> Optional[Dict[str, Any]]:
    if not identifier:
        return None
    # Section 4.2: Catalogue lookup must use stable identifiers: task_code -> template_id -> activity_id.
    # Never use an attempt UUID for translation lookup.
    if is_uuid(identifier):
        return None
    return GOVERNED_ACTIVITY_CATALOG.get(identifier)


def validate_activity_localization(task_or_dict: Any, requested_locale: str = "si") -> Dict[str, Any]:
    """
    Implements availability reporting.
    Never silently copies English into a field labeled si.
    Sinhala status cannot be AVAILABLE if required Sinhala fields are missing.
    """
    norm_locale = "si" if requested_locale.lower().startswith("si") else "en"
    if norm_locale == "en":
        return {
            "requested_locale": "en",
            "content_available": True,
            "missing_localized_fields": []
        }

    code = getattr(task_or_dict, "task_code", None) or (task_or_dict.get("task_code") if isinstance(task_or_dict, dict) else None)
    cat = get_governed_activity_localization(code) if code else (task_or_dict if isinstance(task_or_dict, dict) and "title" in task_or_dict and "instruction" in task_or_dict else None)

    missing_fields = []

    # Title check
    has_si_title = False
    if cat and isinstance(cat.get("title"), dict) and cat["title"].get("si"):
        has_si_title = True
    elif hasattr(task_or_dict, "title_si") and getattr(task_or_dict, "title_si"):
        has_si_title = True
    elif isinstance(task_or_dict, dict) and task_or_dict.get("title_si"):
        has_si_title = True
    elif isinstance(task_or_dict, dict) and isinstance(task_or_dict.get("title"), dict) and task_or_dict["title"].get("si"):
        has_si_title = True
    if not has_si_title:
        missing_fields.append("title.si")

    # Instruction check
    has_si_instruction = False
    if cat and isinstance(cat.get("instruction"), dict) and cat["instruction"].get("si"):
        has_si_instruction = True
    elif hasattr(task_or_dict, "instruction_si") and getattr(task_or_dict, "instruction_si"):
        has_si_instruction = True
    elif isinstance(task_or_dict, dict) and task_or_dict.get("instruction_si"):
        has_si_instruction = True
    elif isinstance(task_or_dict, dict) and isinstance(task_or_dict.get("instruction"), dict) and task_or_dict["instruction"].get("si"):
        has_si_instruction = True
    if not has_si_instruction:
        missing_fields.append("instruction.si")

    # Target skill check
    target_skill = (cat.get("target_skill") if cat else None) or getattr(task_or_dict, "target_skill_details", None) or (task_or_dict.get("target_skill_details") if isinstance(task_or_dict, dict) else None) or getattr(task_or_dict, "target_skill", None) or (task_or_dict.get("target_skill") if isinstance(task_or_dict, dict) else None)
    if isinstance(target_skill, dict) and "label" in target_skill:
        lbl = target_skill["label"]
        if isinstance(lbl, dict) and (not lbl.get("si") or not str(lbl.get("si")).strip()):
            missing_fields.append("target_skill.label.si")
    elif cat and "target_skill" not in cat:
        missing_fields.append("target_skill.label.si")

    # Tokens check
    tokens = (cat.get("tokens") if cat else None) or getattr(task_or_dict, "tokens", None) or (task_or_dict.get("tokens") if isinstance(task_or_dict, dict) else None)
    if tokens and isinstance(tokens, list):
        for idx, tok in enumerate(tokens):
            tok_text = tok.get("text") if isinstance(tok, dict) else getattr(tok, "text", None)
            si_text = tok_text.get("si") if isinstance(tok_text, dict) else getattr(tok_text, "si", None)
            if not si_text or not str(si_text).strip():
                tok_id = (tok.get("token_id") if isinstance(tok, dict) else getattr(tok, "token_id", None)) or f"token_{idx}"
                missing_fields.append(f"tokens.{tok_id}.si")

    # Options check
    options = (cat.get("options") if cat else None) or getattr(task_or_dict, "options", None) or (task_or_dict.get("options") if isinstance(task_or_dict, dict) else None)
    if options and isinstance(options, list):
        for idx, opt in enumerate(options):
            if isinstance(opt, dict) and "label" in opt:
                opt_lbl = opt["label"]
                if isinstance(opt_lbl, dict) and (not opt_lbl.get("si") or not str(opt_lbl.get("si")).strip()):
                    opt_id = opt.get("id", f"opt_{idx}")
                    missing_fields.append(f"options.{opt_id}.si")

    is_available = len(missing_fields) == 0
    return {
        "requested_locale": norm_locale,
        "content_available": is_available,
        "missing_localized_fields": missing_fields
    }


def enrich_task_localization(task: Any) -> Any:
    """Enriches a Task model or dictionary with canonical multilingual activity fields."""
    code = getattr(task, "task_code", None) or (task.get("task_code") if isinstance(task, dict) else None)
    cat = get_governed_activity_localization(code)
    val_report = validate_activity_localization(task, "si") if cat else {
        "requested_locale": "si", "content_available": False, "missing_localized_fields": ["instruction.si", "title.si"]
    }
    si_available = val_report["content_available"]

    if cat:
        title_dict = cat["title"]
        inst_dict = cat["instruction"]
        desc_dict = cat.get("description")
        act_type = cat.get("activity_type")
        tokens_list = cat.get("tokens")
        ts_details = cat.get("target_skill") if isinstance(cat.get("target_skill"), dict) else None
        status_map = {
            "en": "AVAILABLE",
            "si": "AVAILABLE" if si_available else "UNAVAILABLE"
        }
    else:
        orig_title = getattr(task, "title", "") if not isinstance(task, dict) else task.get("title", "")
        orig_inst = (getattr(task, "child_friendly_instruction", None) or getattr(task, "original_instruction", "")) if not isinstance(task, dict) else (task.get("child_friendly_instruction") or task.get("original_instruction", ""))
        orig_type = getattr(task, "task_type", "vocabulary") if not isinstance(task, dict) else task.get("task_type", "vocabulary")
        title_dict = {"en": orig_title, "si": None}
        inst_dict = {"en": orig_inst, "si": None}
        desc_dict = None
        act_type = {"en": orig_type, "si": None} if orig_type else None
        tokens_list = None
        ts_details = None
        status_map = {"en": "AVAILABLE", "si": "UNAVAILABLE"}

    if isinstance(task, dict):
        task["activity_id"] = task.get("id") or code
        task["task_code"] = code
        task["template_id"] = code
        task["title"] = title_dict
        task["title_en"] = title_dict.get("en")
        task["title_si"] = title_dict.get("si")
        task["instruction"] = inst_dict
        task["instruction_en"] = inst_dict.get("en")
        task["instruction_si"] = inst_dict.get("si")
        task["localized_title"] = title_dict
        task["localized_instruction"] = inst_dict
        task["description"] = desc_dict
        task["activity_type"] = act_type
        task["tokens"] = tokens_list
        task["target_skill_details"] = ts_details
        task["content_language_status"] = status_map
        task["content_availability"] = val_report
    else:
        setattr(task, "activity_id", getattr(task, "id", None) or code)
        setattr(task, "task_code", code)
        setattr(task, "template_id", code)
        setattr(task, "title_en", title_dict.get("en"))
        setattr(task, "title_si", title_dict.get("si"))
        setattr(task, "instruction_en", inst_dict.get("en"))
        setattr(task, "instruction_si", inst_dict.get("si"))
        setattr(task, "localized_title", title_dict)
        setattr(task, "localized_instruction", inst_dict)
        setattr(task, "description", desc_dict)
        setattr(task, "activity_type", act_type)
        setattr(task, "tokens", tokens_list)
        setattr(task, "target_skill_details", ts_details)
        setattr(task, "content_language_status", status_map)
        setattr(task, "content_availability", val_report)

    return task


def enrich_attempt_localization(attempt: Any, task: Any, support_level: Optional[str] = None) -> Any:
    """Enriches an Attempt model or dictionary with canonical multilingual activity fields."""
    code = (getattr(task, "task_code", None) if task else None) or getattr(attempt, "task_code", None)
    cat = get_governed_activity_localization(code) if code else None
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

    val_report = validate_activity_localization(task or cat or attempt, "si") if (cat or task) else {
        "requested_locale": "si", "content_available": False, "missing_localized_fields": ["instruction.si"]
    }
    si_available = val_report["content_available"]

    status_map = {
        "en": "AVAILABLE",
        "si": "AVAILABLE" if si_available else "UNAVAILABLE"
    }

    if cat:
        attempt.activity_id = getattr(task, "id", None) or code
        attempt.template_id = code
        attempt.task_code = code
        attempt.title = cat["title"]
        attempt.instruction = {
            "en": presented_inst or cat["instruction"]["en"],
            "si": si_instruction
        } if si_instruction else {"en": presented_inst or cat["instruction"]["en"]}
        attempt.instruction_si = si_instruction
        attempt.presented_instruction_si = si_instruction
        attempt.options = cat.get("options")
        attempt.tokens = cat.get("tokens")
        attempt.activity_type = cat.get("activity_type")
        attempt.description = cat.get("description")
        attempt.target_skill_details = cat.get("target_skill") if isinstance(cat.get("target_skill"), dict) else None
        attempt.content_language_status = status_map
        attempt.content_availability = val_report
    else:
        orig_title = getattr(task, "title", "") if task else ""
        attempt.activity_id = getattr(task, "id", None) if task else None
        attempt.template_id = code
        attempt.task_code = code
        attempt.title = {"en": orig_title}
        attempt.instruction = {"en": presented_inst}
        attempt.instruction_si = None
        attempt.presented_instruction_si = None
        attempt.options = getattr(task, "options", None) if task else None
        attempt.tokens = None
        attempt.activity_type = None
        attempt.description = None
        attempt.target_skill_details = None
        attempt.content_language_status = {"en": "AVAILABLE", "si": "UNAVAILABLE"}
        attempt.content_availability = val_report

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
    code = (
        (task.get("task_code") if isinstance(task, dict) else getattr(task, "task_code", None))
        if task else None
    ) or (
        (attempt.get("task_code") if isinstance(attempt, dict) else getattr(attempt, "task_code", None))
        if attempt else None
    )
    cat = get_governed_activity_localization(code) if code else None
    level = (attempt.get("support_level") if isinstance(attempt, dict) else getattr(attempt, "support_level", "moderate")) if attempt else "moderate"
    presented_inst = view.get("presented_instruction", "")

    val_report = validate_activity_localization(task or cat, "si") if (cat or task) else {
        "requested_locale": "si", "content_available": False, "missing_localized_fields": ["instruction.si"]
    }
    si_available = val_report["content_available"]

    si_instruction = None
    if cat:
        if "support_versions" in cat and level in cat["support_versions"]:
            si_instruction = cat["support_versions"][level].get("si")
        if not si_instruction and "instruction" in cat:
            si_instruction = cat["instruction"].get("si")

        task_id = (task.get("id") if isinstance(task, dict) else getattr(task, "id", None)) if task else None
        view["activity_id"] = task_id or code
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
        view["tokens"] = cat.get("tokens") or (task.get("tokens") if isinstance(task, dict) else getattr(task, "tokens", None))
        view["activity_type"] = cat.get("activity_type")
        view["description"] = cat.get("description")
        view["target_skill_details"] = cat.get("target_skill") if isinstance(cat.get("target_skill"), dict) else None
        view["content_language_status"] = {
            "en": "AVAILABLE",
            "si": "AVAILABLE" if si_available else "UNAVAILABLE"
        }
        view["content_availability"] = val_report
    else:
        view["activity_id"] = getattr(task, "id", None) if task else None
        view["template_id"] = code
        view["task_code"] = code
        view["title"] = {"en": getattr(task, "title", "")} if task else None
        view["instruction"] = {"en": presented_inst}
        view["instruction_si"] = None
        view["presented_instruction_si"] = None
        view["tokens"] = None
        view["activity_type"] = None
        view["description"] = None
        view["target_skill_details"] = None
        view["content_language_status"] = {"en": "AVAILABLE", "si": "UNAVAILABLE"}
        view["content_availability"] = val_report

    return view

