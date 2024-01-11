from huggingface_hub import snapshot_download
import requests
from PIL import Image

def download_model(repo_id, token=None):
    local_dir = f"model/{repo_id.split('/')[-1]}"
    snapshot_download(repo_id=repo_id, token=token, allow_patterns=["*.bin", "*.json", "*.model", "*.txt"], local_dir=local_dir, local_dir_use_symlinks=False)

def download_image():
    img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg' 
    image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
    image.save('demo.jpg')

download_model('Salesforce/blip-image-captioning-large')
download_image()