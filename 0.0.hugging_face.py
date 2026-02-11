# hf_download_annotations.py
import os
from huggingface_hub import login, hf_hub_download

# ====== EDIT THESE 3 ======
TOKEN   = ""     # your HF token (Read)
REPO_ID = "chendelong/MEP-3M"         # e.g. "someone/mep-3m-mirror"
FILENAME = "annotations.json"              # or "annotations.jsonl"
# ===========================

OUT_DIR = "MEP3M_ANN"
os.makedirs(OUT_DIR, exist_ok=True)

# "Normal login" (stores token in HF cache, same as CLI login)
login(token=TOKEN)

# Download ONLY the file you want
path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    repo_type="dataset",
    local_dir=OUT_DIR,
    local_dir_use_symlinks=False,
)

print(" Downloaded:", path)
