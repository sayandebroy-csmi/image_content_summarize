import requests

def test_summarize_api(image_path):
    url = 'http://localhost:5000/summarize'
    
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        print("Success!")
        print("Summary:", response.json()['summary'])
    else:
        print("Error:")
        print("Status code:", response.status_code)
        print("Response:", response.text)

test_summarize_api('uploads/image1.png')