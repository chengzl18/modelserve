import requests
import concurrent.futures
import time


def make_request(request_id):
    from PIL import Image
    from io import BytesIO

    url = 'http://localhost:8888/custom'

    # Convert the image to bytes
    image = Image.open('demo.jpg')
    image_byte_array = BytesIO()
    image.save(image_byte_array, format='PNG')
    image_data = image_byte_array.getvalue()

    files = {'image': ('demo.jpg', image_data)}

    try:
        response = requests.post(url, files=files)
        return response.status_code == 200
    except Exception as e:
        return False

# Parameters for the test
num_requests = 100  # Number of requests to make
max_workers = 25    # Number of concurrent workers

# Start the test
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    results = list(executor.map(make_request, range(num_requests)))

# Calculate results
end_time = time.time()
total_time = end_time - start_time
successful_requests = results.count(True)
failed_requests = results.count(False)
requests_per_second = successful_requests / total_time

# Output the results
print(f'Total Time: {total_time:.2f} seconds')
print(f'Successful Requests: {successful_requests}')
print(f'Failed Requests: {failed_requests}')
print(f'Requests Per Second: {requests_per_second:.2f}')