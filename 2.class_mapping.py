import json
from collections import defaultdict
from pathlib import Path

# ===== CONFIG =====
INPUT_JSON = "annotations_output.json"     # change to your file, e.g. "MEP3M_ANN/annotations.json"
OUTPUT_TXT = "class_hierarchy.txt"
# ==================

def norm_false(x):
    if x is None:
        return None
    if isinstance(x, str) and x.strip().upper() == "FALSE":
        return None
    return x

# class -> sub -> set(subsub)
# We'll store names too for readability
hier = defaultdict(lambda: defaultdict(set))

# Store name mappings (to print consistently)
class_names = {}
sub_names = {}
subsub_names = {}

print("📥 Loading JSON...")
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)  # expects a list of dicts

print(f"🔎 Records: {len(data)}")
print("🧠 Building hierarchy...")

for item in data:
    c_id = str(item.get("class_id")).strip()
    s_id = str(item.get("sub_class_id")).strip()

    c_name = (item.get("class_name") or "").strip()
    s_name = (item.get("sub_class_name") or "").strip()

    class_names[c_id] = c_name or class_names.get(c_id, "")
    sub_names[(c_id, s_id)] = s_name or sub_names.get((c_id, s_id), "")

    ss_id_raw = norm_false(item.get("subsub_class_id"))
    ss_name_raw = norm_false(item.get("subsub_class_name"))

    if ss_id_raw is not None and ss_name_raw is not None:
        ss_id = str(ss_id_raw).strip()
        ss_name = str(ss_name_raw).strip()
        subsub_names[(c_id, s_id, ss_id)] = ss_name or subsub_names.get((c_id, s_id, ss_id), "")
        hier[c_id][s_id].add(ss_id)
    else:
        # still record that class->sub exists even if no subsub
        _ = hier[c_id][s_id]

# ---- Write TXT ----
print(f"💾 Writing: {OUTPUT_TXT}")

lines = []
lines.append("MEP-3M CLASS HIERARCHY (class -> sub_class -> subsub_class)\n")
lines.append(f"Total classes: {len(hier)}\n")

for c_id in sorted(hier.keys(), key=lambda x: int(x) if x.isdigit() else x):
    c_name = class_names.get(c_id, "")
    lines.append(f"CLASS {c_id}: {c_name}")

    subs = hier[c_id]
    for s_id in sorted(subs.keys(), key=lambda x: int(x) if x.isdigit() else x):
        s_name = sub_names.get((c_id, s_id), "")
        lines.append(f"  └─ SUB {s_id}: {s_name}")

        subsubs = subs[s_id]
        if not subsubs:
            lines.append("       └─ SUBSUB: (none)")
        else:
            for ss_id in sorted(subsubs, key=lambda x: int(x) if x.isdigit() else x):
                ss_name = subsub_names.get((c_id, s_id, ss_id), "")
                lines.append(f"       └─ SUBSUB {ss_id}: {ss_name}")

    lines.append("")  # blank line between classes

Path(OUTPUT_TXT).write_text("\n".join(lines), encoding="utf-8")

print("✅ Done.")
print(f"📄 Saved to: {OUTPUT_TXT}")
