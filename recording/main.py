import json
from symbol import continue_stmt

import sseclient
import requests
import sys

# URL of the SSE endpoint
sse_url = 'http://192.168.4.1/uart0'

# Function to process the SSE data and save it to a JSON file
def process_sse_data():
    # Open a connection to the SSE endpoint
    # response = requests.get(sse_url, stream=True)
    # if response.status_code != 200:
    #     print(f"Error: Unable to connect to {sse_url}, status code: {response.status_code}")
    #     return

    client = sseclient.SSEClient(sse_url)

    # List to store x/y time data
    xy_time_data = []

    print("client connected")

    try:
        for event in client:
            try:
                # Parse the event data (assuming it's JSON formatted)
                data = json.loads(event.data)

                time_stamp = data["time"]

                dataArray = []

                for item in data["data"]:
                    dataArray.append({"x": item[0], "y": item[1], "t": item[2]})

                # Append the data to the list
                xy_time_data.append({"time": time_stamp, "data": dataArray})

                # Print the received data (optional)
                print(f"Received data: time={time_stamp}")

            except:
                print("Failed to decode JSON data from SSE event")
    # break in the case of a keyboard end
    except KeyboardInterrupt:
        print("Cntl+C, exiting")

    # Save x/y time data to JSON file
    fileName = 'xy_time_data.json'
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

    with open(fileName, 'w') as json_file:
        json.dump({"data": xy_time_data}, json_file, indent=4)

    print(f"x/y time data saved to '{fileName}'.")

if __name__ == "__main__":
    process_sse_data()