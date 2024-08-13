import requests

# Replace this with the actual URL where your Flask API is running
api_url = "http://localhost:5000/get_max_data"

# Make a GET request to the API
response = requests.get(api_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    result_json = response.json()

    # Now you can work with the data as needed
    print(result_json)
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}, {response.text}")
    