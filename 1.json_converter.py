# translate_annotations_keep_keys.py
# Goal:
# - Keep ALL keys exactly the same
# - For each value:
#   - if it's Chinese/foreign -> translate to English
#   - if it's already English/ASCII -> leave it unchanged


import json
import re
from typing import Any, Dict, List
from tqdm import tqdm
from deep_translator import GoogleTranslator

# ====== CONFIG ======
INPUT_JSON = "annotations-1k.json"
OUTPUT_JSON = "annotations_output.json"

translator = GoogleTranslator(source="auto", target="en")

# Detect CJK (Chinese/Japanese/Korean) characters
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")  # CJK Unified Ideographs + Extension A

def is_foreign_text(s: str) -> bool:
    """
    Returns True if string likely contains Chinese (or other non-ASCII) characters
    that we want to translate.
    - If it contains CJK -> translate
    - Else if it has lots of non-ASCII letters (e.g., accented languages) -> translate
    - Otherwise treat as English/already OK
    """
    if not s or not isinstance(s, str):
        return False

    s = s.strip()
    if not s:
        return False

    # Common sentinel used in MEP annotations
    if s.upper() == "FALSE":
        return False

    # If Chinese characters exist -> translate
    if CJK_RE.search(s):
        return True

    # If mostly ASCII, assume English/OK (brand names etc.)
    ascii_ratio = sum(1 for ch in s if ord(ch) < 128) / max(1, len(s))
    if ascii_ratio > 0.90:
        return False

    # Otherwise it's probably a foreign language (or noisy OCR) -> translate
    return True

def safe_translate(s: str) -> str:
    """Translate with fallback to original on any error."""
    try:
        return translator.translate(s)
    except Exception:
        return s

def translate_value(v: Any) -> Any:
    """
    Translate only string values. Keep:
    - numbers as numbers
    - lists (e.g., img_resolution) as-is
    - paths as-is (they are ASCII, will be skipped)
    """
    if isinstance(v, str):
        if is_foreign_text(v):
            return safe_translate(v)
        return v
    return v

def translate_record_keep_keys(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dict with SAME keys, translated values when needed."""
    out = {}
    for k, v in rec.items():
        # Keep lists/dicts unchanged except translating inner strings if you want.
        # Here: only translate top-level string fields (title, class_name, etc.)
        out[k] = translate_value(v)
    return out


# -------- RUN --------
print("📥 Loading JSON...")
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data: List[Dict[str, Any]] = json.load(f)

print(f"🔎 Records: {len(data)}")
print("🌍 Translating (keys unchanged)...")

translated = []
for rec in tqdm(data):
    translated.append(translate_record_keep_keys(rec))

print("💾 Saving...")
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(translated, f, ensure_ascii=False, indent=2)

print("✅ DONE")
print(f"📤 Output: {OUTPUT_JSON}")
print("\nExample output row:\n", json.dumps(translated[0], ensure_ascii=False, indent=2))
