from huggingface_hub import snapshot_download

def download_model(repo_id, token=None):
    local_dir = f"model/{repo_id.split('/')[-1]}"
    snapshot_download(repo_id=repo_id, token=token, allow_patterns=["*.bin", "*.json", "*.model", "*.txt"], local_dir=local_dir, local_dir_use_symlinks=False)

download_model('google/flan-t5-base')