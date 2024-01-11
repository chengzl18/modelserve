import requests

text = 'translate English to German: How old are you?'
url = 'http://localhost:8888/custom?text=' + text

response = requests.get(url)

# Check the response
if response.status_code == 200:
    # Request was successful
    data = response.json()
    results = data['text']
    print(f'Results: {results}')
else:
    print(f'Failed to make the request. Status code: {response.status_code}')