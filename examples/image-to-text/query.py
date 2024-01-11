import requests
from PIL import Image
from io import BytesIO

url = 'http://localhost:8888/custom'

# Convert the image to bytes
image = Image.open('demo.jpg')
image_byte_array = BytesIO()
image.save(image_byte_array, format='PNG')
image_data = image_byte_array.getvalue()

files = {'image': ('demo.jpg', image_data)}
response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    # Request was successful
    data = response.json()
    results = data['text']
    print(f'Results: {results}')
else:
    print(f'Failed to make the request. Status code: {response.status_code}')