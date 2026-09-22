import re
from typing import Dict, Any, Optional, List
from app.database.models import Task, LearnerProfile, Attempt
from app.generation.base import BaseInstructionGenerator
from app.tasks.repository import task_repository

class RuleGenerator(BaseInstructionGenerator):
    """
    Deterministic 100% offline child-friendly rule generator.
    Implements:
    1. Single-action focus & sentence-splitting across attempts.
    2. Strict sentence length enforcement (target <= 8-10 words, strict max 12 words).
    3. Age-graded vocabulary replacement using expert-reviewed CEFR dictionary.
    4. Non-punitive, warm supportive encouragement.
    5. Support-level-aligned visual cues and answer formats.
    """

    def __init__(self):
        # Curated developmental templates for all 10 seed tasks
        self.task_templates = {
            "TASK-ENG-001": {  # Classroom cleanup (two-step)
                1: {
                    "mild": "Put your crayons in the box.",
                    "moderate": "First, put your crayons in the box.",
                    "strong": "Put your crayons in the box.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["highlight_crayons", "show_crayon_box"]
                },
                2: {
                    "mild": "Now put the paper in the green bin.",
                    "moderate": "Put the paper in the green bin.",
                    "strong": "Put the paper in the green bin.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["highlight_paper", "show_green_bin"]
                },
                3: {
                    "mild": "Tap the green bin for the paper.",
                    "moderate": "Tap the green bin for the paper.",
                    "strong": "Tap the green bin.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_green_bin", "point_arrow"]
                }
            },
            "TASK-ENG-002": {  # Animal habitats
                1: {
                    "mild": "Put each animal in its home.",
                    "moderate": "Put each animal in its home.",
                    "strong": "Where does each animal live?",
                    "answer_format": "drag_and_drop",
                    "visual_cues": ["show_animal_cards", "show_habitats"]
                },
                2: {
                    "mild": "Look at the fish. Where does it live?",
                    "moderate": "Where does the fish live?",
                    "strong": "Find where the fish lives.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_fish", "show_water_and_tree"]
                },
                3: {
                    "mild": "Choose: does fish live in water or tree?",
                    "moderate": "Choose: does fish live in water or tree?",
                    "strong": "Look at fish. Choose: water or tree?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_water_card", "show_tree_card", "point_water"]
                }
            },
            "TASK-ENG-003": {  # Big and small object sorting
                1: {
                    "mild": "Put the big ball in the blue box.",
                    "moderate": "Put the big ball in the blue box.",
                    "strong": "Find the big blue ball.",
                    "answer_format": "drag_and_drop",
                    "visual_cues": ["highlight_big_ball", "show_blue_box"]
                },
                2: {
                    "mild": "Find the big blue ball and place it.",
                    "moderate": "Put the big ball in the box.",
                    "strong": "Put the big ball in the box.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["highlight_big_ball", "glowing_blue_box"]
                },
                3: {
                    "mild": "Touch the big blue ball.",
                    "moderate": "Touch the big blue ball.",
                    "strong": "Touch the big blue ball.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["point_big_ball", "dim_small_balls"]
                }
            },
            "TASK-ENG-004": {  # Fruit and vegetable identification
                1: {
                    "mild": "Find all the green vegetables.",
                    "moderate": "Find all the green vegetables.",
                    "strong": "Look at the food. Find green vegetables.",
                    "answer_format": "tap_selection",
                    "visual_cues": ["highlight_food_tray"]
                },
                2: {
                    "mild": "Look at the broccoli. Is it a vegetable?",
                    "moderate": "Is the broccoli a vegetable?",
                    "strong": "Find the broccoli.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_broccoli", "show_apple"]
                },
                3: {
                    "mild": "Point to the broccoli.",
                    "moderate": "Point to the broccoli.",
                    "strong": "Touch the green broccoli.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["point_broccoli", "sparkle_broccoli"]
                }
            },
            "TASK-ENG-005": {  # Three-step morning sequence
                1: {
                    "mild": "First, brush your teeth.",
                    "moderate": "First, brush your teeth.",
                    "strong": "Show what we do first: brush teeth.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["highlight_toothbrush", "show_step_1"]
                },
                2: {
                    "mild": "Next, wash your face.",
                    "moderate": "Next, wash your face.",
                    "strong": "Wash your face.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["highlight_washcloth", "show_step_2"]
                },
                3: {
                    "mild": "Tap the picture of washing your face.",
                    "moderate": "Tap the picture of washing your face.",
                    "strong": "Tap washing your face.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_wash_face", "point_step_2"]
                }
            },
            "TASK-ENG-006": {  # Preposition placement
                1: {
                    "mild": "Put the small cat under the desk.",
                    "moderate": "Put the cat under the desk.",
                    "strong": "Put the cat under the desk.",
                    "answer_format": "drag_and_drop",
                    "visual_cues": ["highlight_cat", "show_under_desk"]
                },
                2: {
                    "mild": "Where is the cat? Put it under desk.",
                    "moderate": "Put the cat under the desk.",
                    "strong": "Put the cat under the desk.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["highlight_under_desk_area"]
                },
                3: {
                    "mild": "Choose: is the cat on or under desk?",
                    "moderate": "Choose: is cat on or under desk?",
                    "strong": "Choose: on or under?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_on_desk_picture", "show_under_desk_picture"]
                }
            },
            "TASK-ENG-007": {  # Color and shape matching
                1: {
                    "mild": "Put the red triangle next to yellow square.",
                    "moderate": "Put the red triangle by yellow square.",
                    "strong": "Find the red triangle.",
                    "answer_format": "drag_and_drop",
                    "visual_cues": ["highlight_red_triangle", "highlight_yellow_square"]
                },
                2: {
                    "mild": "Put the red triangle beside the yellow square.",
                    "moderate": "Put red triangle by yellow square.",
                    "strong": "Place red triangle by yellow square.",
                    "answer_format": "tap_and_place",
                    "visual_cues": ["show_red_triangle", "glowing_slot_next_to_square"]
                },
                3: {
                    "mild": "Touch the red triangle.",
                    "moderate": "Touch the red triangle.",
                    "strong": "Touch the red triangle.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["point_red_triangle", "dim_other_shapes"]
                }
            },
            "TASK-ENG-008": {  # Short story comprehension
                1: {
                    "mild": "Who found the shiny key?",
                    "moderate": "Who found the shiny key?",
                    "strong": "Who found the shiny key?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_rabbit_card", "show_bear_card"]
                },
                2: {
                    "mild": "Did the rabbit or bear find the key?",
                    "moderate": "Did rabbit or bear find the key?",
                    "strong": "Look: rabbit or bear found the key?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_rabbit", "highlight_bear"]
                },
                3: {
                    "mild": "Choose: the rabbit or the bear?",
                    "moderate": "Choose: the rabbit or the bear?",
                    "strong": "Choose: rabbit or bear?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["point_rabbit", "point_bear"]
                }
            },
            "TASK-ENG-009": {  # Pronoun picture choice
                1: {
                    "mild": "Look at the girl. Choose: he or she?",
                    "moderate": "Look at the girl. Choose: he or she?",
                    "strong": "Look at girl. Choose: he or she?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_girl_kicking", "show_pronoun_cards"]
                },
                2: {
                    "mild": "She is playing. Choose the word: She.",
                    "moderate": "She is playing. Choose: She.",
                    "strong": "Choose the word: She.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_she_card", "show_girl_photo"]
                },
                3: {
                    "mild": "Touch the word: She.",
                    "moderate": "Touch the word: She.",
                    "strong": "Touch the word: She.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_she_card", "point_she"]
                }
            },
            "TASK-ENG-010": {  # AR garden planting explorer
                1: {
                    "mild": "Put the seeds into the soft dirt.",
                    "moderate": "Put the seeds into the soft dirt.",
                    "strong": "Put seeds in the dirt.",
                    "answer_format": "drag_and_drop",
                    "visual_cues": ["highlight_seed_packet", "show_pot_dirt"]
                },
                2: {
                    "mild": "Now pour water on the dirt.",
                    "moderate": "Now pour water on the dirt.",
                    "strong": "Pour water on the dirt.",
                    "answer_format": "tap_and_hold",
                    "visual_cues": ["highlight_watering_can", "show_water_droplets"]
                },
                3: {
                    "mild": "Tap the glowing watering can.",
                    "moderate": "Tap the glowing watering can.",
                    "strong": "Tap the watering can.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_watering_can", "point_can"]
                }
            },

            # ── Grammar tasks ──────────────────────────────────────────────

            "GRAM-ART-001": {  # Indefinite article: a vs an (answer: "an")
                1: {
                    "mild": "Which word comes before 'apple': a or an?",
                    "moderate": "Choose: a or an? — before 'apple'.",
                    "strong": "Touch the right word before 'apple'.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_a_card", "show_an_card", "highlight_apple_image"]
                },
                2: {
                    "mild": "Say the words: 'an apple'. Which sounds right?",
                    "moderate": "Which sounds right: 'a apple' or 'an apple'?",
                    "strong": "Choose: 'a apple' or 'an apple'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_a_card", "show_an_card", "highlight_correct_sound"]
                },
                3: {
                    "mild": "Touch the word 'an' to go before apple.",
                    "moderate": "Touch the word 'an'.",
                    "strong": "Touch 'an'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_an_card", "point_an"]
                }
            },

            "GRAM-PREP-001": {  # Location preposition: fish lives IN water
                1: {
                    "mild": "Where does the fish live? Choose the right word.",
                    "moderate": "Choose the word that tells where fish lives.",
                    "strong": "Touch the word for where fish lives.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_fish_image", "show_water_image", "show_preposition_cards"]
                },
                2: {
                    "mild": "Does the fish live 'in' water or 'on' water?",
                    "moderate": "Choose: 'in' or 'on' for the fish?",
                    "strong": "Choose: 'in' or 'on'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_in_card", "highlight_on_card", "show_fish_in_water"]
                },
                3: {
                    "mild": "Touch the word 'in' — the fish lives in water.",
                    "moderate": "Touch the word 'in'.",
                    "strong": "Touch 'in'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_in_card", "point_in", "show_fish_in_water"]
                }
            },

            "GRAM-SVA-001": {  # Subject-verb agreement: He plays with the ball.
                1: {
                    "mild": "Listen: does 'He play' or 'He plays' sound right?",
                    "moderate": "Choose the right sentence about the boy.",
                    "strong": "Touch the right sentence.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_boy_with_ball", "show_sentence_cards"]
                },
                2: {
                    "mild": "Which sounds right: 'He play' or 'He plays'?",
                    "moderate": "Choose: 'He play' or 'He plays'?",
                    "strong": "Choose: 'play' or 'plays'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_play_card", "highlight_plays_card", "show_boy_image"]
                },
                3: {
                    "mild": "Touch the word 'plays' to make the sentence right.",
                    "moderate": "Touch the word 'plays'.",
                    "strong": "Touch 'plays'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_plays_card", "point_plays"]
                }
            },

            "GRAM-PRON-001": {  # Subject pronoun: She (for girl)
                1: {
                    "mild": "Look at the girl. Do we say 'he' or 'she'?",
                    "moderate": "Choose the right word for the girl.",
                    "strong": "Touch the right word for the girl.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_girl_image", "show_he_card", "show_she_card"]
                },
                2: {
                    "mild": "The girl is running. Choose: 'he' or 'she'?",
                    "moderate": "Choose: 'he' or 'she' for the girl?",
                    "strong": "Choose: 'he' or 'she'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_she_card", "highlight_he_card", "highlight_girl_image"]
                },
                3: {
                    "mild": "Touch the word 'she' for the girl.",
                    "moderate": "Touch the word 'she'.",
                    "strong": "Touch 'she'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_she_card", "point_she", "show_girl_image"]
                }
            },

            "GRAM-PLUR-001": {  # Plural: dog → dogs
                1: {
                    "mild": "There are three dogs. Say the right word for many dogs.",
                    "moderate": "Choose the word for many dogs.",
                    "strong": "Touch the right word for many dogs.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_three_dogs_image", "show_dog_card", "show_dogs_card"]
                },
                2: {
                    "mild": "Is it 'dog' or 'dogs' when there are three?",
                    "moderate": "Choose: 'dog' or 'dogs' for three?",
                    "strong": "Choose: 'dog' or 'dogs'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_dogs_card", "highlight_dog_card", "show_count_3"]
                },
                3: {
                    "mild": "Touch the word 'dogs' for three animals.",
                    "moderate": "Touch the word 'dogs'.",
                    "strong": "Touch 'dogs'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_dogs_card", "point_dogs"]
                }
            },

            "GRAM-TENSE-001": {  # Past tense: walk → walked
                1: {
                    "mild": "The boy walked yesterday. Choose the right word.",
                    "moderate": "Choose the past word for 'walk'.",
                    "strong": "Touch the right past word.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_boy_walking_image", "show_walk_card", "show_walked_card"]
                },
                2: {
                    "mild": "Did he 'walk' or 'walked' yesterday?",
                    "moderate": "Choose: 'walk' or 'walked' for yesterday?",
                    "strong": "Choose: 'walk' or 'walked'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_walked_card", "highlight_walk_card", "show_yesterday_cue"]
                },
                3: {
                    "mild": "Touch the word 'walked' for what happened before.",
                    "moderate": "Touch the word 'walked'.",
                    "strong": "Touch 'walked'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_walked_card", "point_walked"]
                }
            },

            "GRAM-COMPL-001": {  # Sentence completion: The clouds are in the ___. (sky)
                1: {
                    "mild": "The clouds are in the ___. What word fits?",
                    "moderate": "Choose a word to finish: The clouds are in the ___.",
                    "strong": "Touch the right word to finish the sentence.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_cloud_image", "show_sky_card", "show_word_choices"]
                },
                2: {
                    "mild": "Are the clouds in the 'sky' or 'floor'?",
                    "moderate": "Choose: 'sky' or 'floor' for the clouds?",
                    "strong": "Choose: 'sky' or 'floor'?",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["highlight_sky_card", "highlight_floor_card", "show_cloud_image"]
                },
                3: {
                    "mild": "Touch the word 'sky' to complete the sentence.",
                    "moderate": "Touch the word 'sky'.",
                    "strong": "Touch 'sky'.",
                    "answer_format": "single_tap_selection",
                    "visual_cues": ["glowing_sky_card", "point_sky", "show_cloud_image"]
                }
            },

            "GRAM-WORD-001": {  # Word ordering: The boy likes apples.
                1: {
                    "mild": "Put the words in the right order: boy, likes, the, apples.",
                    "moderate": "Put these words in order to make a sentence.",
                    "strong": "Touch the words in the right order.",
                    "answer_format": "word_ordering",
                    "visual_cues": ["show_word_tiles", "show_boy_image", "show_apple_image"]
                },
                2: {
                    "mild": "Which comes first — 'The boy' or 'likes apples'?",
                    "moderate": "Put 'The boy' first. Then what comes next?",
                    "strong": "Start with 'The boy'. Touch the next word.",
                    "answer_format": "word_ordering",
                    "visual_cues": ["highlight_the_boy_tile", "show_remaining_tiles", "arrow_next_slot"]
                },
                3: {
                    "mild": "Choose: 'The boy likes apples' or 'Apples likes boy'?",
                    "moderate": "Choose the right sentence.",
                    "strong": "Touch the right sentence.",
                    "answer_format": "two_picture_choice",
                    "visual_cues": ["show_correct_sentence_card", "show_wrong_sentence_card", "glowing_correct"]
                }
            },
        }

    def generate(
        self,
        task: Task,
        learner: LearnerProfile,
        target_attempt_number: int,
        support_level: str,
        previous_attempt: Optional[Attempt] = None,
        previous_observations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes deterministic rule generation with vocabulary replacement and length bounds.
        """
        attempt_idx = min(max(target_attempt_number, 1), 3)
        sup_key = support_level.lower() if support_level in ["mild", "moderate", "strong"] else "mild"
        reason_codes = [f"rule_support_{sup_key}", f"attempt_{attempt_idx}"]

        # 1. Retrieve template or use smart fallback
        if task.task_code in self.task_templates:
            template_cfg = self.task_templates[task.task_code][attempt_idx]
            raw_instruction = template_cfg.get(sup_key, template_cfg.get("mild", task.original_instruction))
            answer_format = template_cfg.get("answer_format", "speech")
            visual_cues = list(template_cfg.get("visual_cues", []))
            reason_codes.append(f"task_template_{task.task_code}")
        else:
            # Smart Fallback for unlisted tasks
            raw_instruction, answer_format, visual_cues = self._generate_fallback(
                task, attempt_idx, sup_key
            )
            reason_codes.append("smart_fallback_rule_applied")

        # 2. Age-graded Vocabulary Replacement Engine
        final_instruction, vocab_support, replaced_codes = self._apply_vocabulary_replacements(
            raw_instruction, learner.age
        )
        reason_codes.extend(replaced_codes)

        # 3. Sentence Length Verification & Hard Limit Enforcement (Target <= 8-10 words, max 12 words)
        final_instruction = self._enforce_sentence_length(final_instruction)

        # 4. Generate Non-Punitive Warm Supportive Phrasing
        supportive_message = self._generate_supportive_message(attempt_idx, sup_key)

        return {
            "child_instruction": final_instruction,
            "supportive_message": supportive_message,
            "vocabulary_support": vocab_support,
            "answer_format": answer_format,
            "visual_cues": visual_cues,
            "reason_codes": reason_codes,
            "generation_method": "rule"
        }

    def _apply_vocabulary_replacements(self, text: str, learner_age: int):
        """Replaces difficult words from seed vocabulary dictionary if learner is below minimum age."""
        vocab_items = task_repository.get_vocabulary_dictionary()
        vocab_support = []
        reason_codes = []
        adapted_text = text

        for item in vocab_items:
            target_word = item["word"]
            # Check whole-word boundary
            pattern = re.compile(rf"\b{re.escape(target_word)}\b", re.IGNORECASE)
            if pattern.search(adapted_text) and learner_age < item.get("minimum_age", 7):
                replacement = item["simple_alternative"]
                
                # Preserve capitalization
                def replace_case(match):
                    m = match.group(0)
                    if m.isupper():
                        return replacement.upper()
                    if m[0].isupper():
                        return replacement.capitalize()
                    return replacement.lower()

                adapted_text = pattern.sub(replace_case, adapted_text)
                vocab_support.append({
                    "word": replacement,
                    "original_word": target_word,
                    "simple_meaning": item.get("simple_definition", "simple word")
                })
                reason_codes.append(f"vocabulary_replaced_{target_word}_with_{replacement}")

        return adapted_text, vocab_support, reason_codes

    def _enforce_sentence_length(self, text: str) -> str:
        """
        Ensures instruction strictly obeys target <= 8-10 words and maximum 12 words per sentence.
        If a sentence exceeds 12 words, trims down to the core action clause.
        """
        # Split on sentence delimiters (., !, ?)
        sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
        trimmed_sentences = []

        for s in sentences:
            words = s.split()
            if len(words) > 12:
                # Truncate to first 10 words for safety
                trimmed_s = " ".join(words[:10])
                trimmed_sentences.append(trimmed_s)
            else:
                trimmed_sentences.append(s)

        total_words = sum(len(s.split()) for s in trimmed_sentences)
        if total_words <= 12:
            return text.strip()

        # If combined length exceeds 12 words, prioritize the first sentence
        res = trimmed_sentences[0]
        if not res.endswith((".", "!", "?")):
            res += "."
        return res

    def _generate_supportive_message(self, attempt_number: int, support_level: str) -> str:
        """Generates friendly, encouraging, non-punitive tone for children aged 4-8."""
        if attempt_number == 1:
            if support_level == "mild":
                return "Let's explore together!"
            elif support_level == "moderate":
                return "You can do it! Let's try."
            return "Let's do this step together!"
        elif attempt_number == 2:
            if support_level == "mild":
                return "Good try! Let's look again."
            elif support_level == "moderate":
                return "Nice try! Let's do one small part."
            return "Good job trying! Let's look at this part."
        else: # Attempt 3
            return "Take your time. Let's look together."

    def _generate_fallback(self, task: Task, attempt_number: int, support_level: str):
        """Smart fallback for any arbitrary task instruction."""
        words = task.original_instruction.split()
        if attempt_number == 1:
            inst = " ".join(words[:10])
            fmt = "drag_and_drop" if "put" in task.original_instruction.lower() else "speech"
            cues = ["highlight_active_item"]
        elif attempt_number == 2:
            inst = "Look closely. " + " ".join(words[:8])
            fmt = "two_picture_choice"
            cues = ["highlight_active_item", "show_target_slot"]
        else:
            inst = "Choose the right match."
            fmt = "single_tap_selection"
            cues = ["point_target", "dim_distractors"]

        if not inst.endswith((".", "!", "?")):
            inst += "."

        return inst, fmt, cues

rule_generator = RuleGenerator()
