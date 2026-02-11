from huggingface_hub import HfApi

REPO_ID = "chendelong/MEP-3M"

api = HfApi()
files = api.list_repo_files(repo_id=REPO_ID, repo_type="dataset")

print(f"Found {len(files)} files/folders:\n")
for f in files:
    print(f)

 