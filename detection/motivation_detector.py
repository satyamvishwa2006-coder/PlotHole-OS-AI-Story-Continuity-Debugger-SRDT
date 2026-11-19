import re
from typing import List, Dict, Any
from utils.helpers import get_val

class MotivationDetector:
    """Detects character motivation contradictions and unearned loyalty/goal reversals."""

    VOW_OF_ENMITY_PATTERNS = [
        r'\b(?:swear|vow|promise)\s+(?:revenge|to kill|to destroy|i will never forgive|i will make you pay)\b',
        r'\b(?:murdered|killed)\s+my\s+(?:brother|sister|father|mother|family|partner)\b',
        r'\b(?:i will never work for you|i will die before i help you)\b'
    ]

    FRIENDLY_COMPLIANCE_PATTERNS = [
        r'\b(?:gladly|happy to help|right away|anything for you|good to see you|loyal)\b',
        r'\b(?:accepts the assignment|smiles warmly|agrees without hesitation)\b'
    ]

    @classmethod
    def detect(cls, scenes: List[Any], characters: List[Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        vows = {}  # char -> {"target": str, "scene": int, "quote": str}

        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            raw_chars = get_val(scene, "characters_present", []) or []
            chars_present = [str(c).upper() for c in raw_chars]

            # 1. Look for sworn enmity or absolute refusal
            for d in get_val(scene, "dialogue_data", []) or []:
                speaker = str(get_val(d, "character", "")).upper()
                text = get_val(d, "text", "") or ""

                for pat in cls.VOW_OF_ENMITY_PATTERNS:
                    if re.search(pat, text, re.I):
                        # Find potential target in scene
                        targets = [c for c in chars_present if c != speaker]
                        vows[speaker] = {
                            "scene": s_num,
                            "quote": f"{speaker}: \"{text}\"",
                            "targets": targets
                        }

            # 2. In subsequent scenes, look for cheerful compliance towards the same characters
            for d in get_val(scene, "dialogue_data", []) or []:
                speaker = str(get_val(d, "character", "")).upper()
                text = get_val(d, "text", "") or ""

                if speaker in vows:
                    vow = vows[speaker]
                    if s_num > vow["scene"]:
                        # Check if targets are present in this scene
                        shared_targets = [t for t in vow["targets"] if t in chars_present]
                        if shared_targets:
                            # Check if speaker is suddenly compliant or warm
                            action_txt = get_val(scene, "action_text", "") or ""
                            for fcp in cls.FRIENDLY_COMPLIANCE_PATTERNS:
                                if re.search(fcp, text, re.I) or re.search(fcp, action_txt, re.I):
                                    issues.append({
                                        "issue_id": f"MOT{issue_count:03d}",
                                        "issue_type": "Motivation Contradiction",
                                        "title": f"Unprompted Motivation Reversal: {speaker} vs {', '.join(shared_targets)}",
                                        "description": (
                                            f"In Scene {vow['scene']}, {speaker} swore mortal vengeance/enmity against {', '.join(shared_targets)}, "
                                            f"yet in Scene {s_num} willingly cooperates or expresses friendly compliance without any narrative catalyst."
                                        ),
                                        "severity": "High",
                                        "confidence": 0.89,
                                        "scene_references": [vow["scene"], s_num],
                                        "evidence": [
                                            {"scene_number": vow["scene"], "text": vow["quote"]},
                                            {"scene_number": s_num, "text": f"Scene {s_num}: \"{text}\""}
                                        ],
                                        "reasoning": (
                                            f"Character agency and consistency are disrupted. {speaker}'s dramatic pledge in Scene {vow['scene']} "
                                            f"is overturned in Scene {s_num} without an intervening apology, blackmail, change of heart, or revelation."
                                        ),
                                        "suggested_fix": (
                                            f"Provide an intervening scene where {speaker} is coerced, manipulated, or secretly plotting double-cross, "
                                            f"or tone down the extreme enmity declared in Scene {vow['scene']}."
                                        )
                                    })
                                    issue_count += 1
                                    del vows[speaker]
                                    break

        return issues
