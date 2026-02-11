import os
import re
from huggingface_hub import HfApi, hf_hub_download
from tqdm import tqdm

# ===== CONFIG =====
REPO_ID = "chendelong/MEP-3M"
OUT_DIR = "MEP3M_IMAGES_RAR"
MAX_PER_RUN = 5

MODE = "even"   # <-- change to "odd" on your friend's machine
# ==================

os.makedirs(OUT_DIR, exist_ok=True)

api = HfApi()
files = api.list_repo_files(repo_id=REPO_ID, repo_type="dataset")

# Collect .rar files
rar_files = [f for f in files if f.lower().endswith(".rar")]

# Extract the number from paths like "Images/101.rar"
num_re = re.compile(r"/(\d+)\.rar$", re.IGNORECASE)

def get_num(path: str):
    m = num_re.search(path.replace("\\", "/"))
    return int(m.group(1)) if m else None

# Keep only properly numbered rars, sorted by number
rar_with_nums = []
for f in rar_files:
    n = get_num(f)
    if n is not None:
        rar_with_nums.append((n, f))

rar_with_nums.sort(key=lambda x: x[0])

# Parity filter
want_even = (MODE.lower() == "even")
assigned = [(n, f) for (n, f) in rar_with_nums if (n % 2 == 0) == want_even]

# Already downloaded locally (by basename)
downloaded = set(os.listdir(OUT_DIR))

# Pending for this parity
pending = [(n, f) for (n, f) in assigned if os.path.basename(f) not in downloaded]

print(f"Total .rar in repo: {len(rar_with_nums)}")
print(f"Your MODE: {MODE} (assigned: {len(assigned)})")
print(f"Already in {OUT_DIR}: {len(downloaded)} files")
print(f"Remaining for your MODE: {len(pending)}")

# Next 5 for your parity
to_download = pending[:MAX_PER_RUN]

if not to_download:
    print("🎉 Nothing left for your MODE to download!")
else:
    print("\n⬇ Downloading:")
    for n, f in to_download:
        print(f"  - {f} (#{n})")

    for n, f in tqdm(to_download, desc=f"Downloading {MODE} batch"):
        hf_hub_download(
            repo_id=REPO_ID,
            repo_type="dataset",
            filename=f,
            local_dir=OUT_DIR,
            local_dir_use_symlinks=False,  # ignored in new hub versions, but fine
        )

    print(f"\n✅ Done. Run again tomorrow for next {MAX_PER_RUN} ({MODE}) files.")

