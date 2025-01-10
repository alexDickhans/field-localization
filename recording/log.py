import json
import sys

# Function to process the log file and save it to a JSON file
def process_log_file(log_file_path):
    # List to store x/y time data
    xy_time_data = []

    try:
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        # Parse the JSON data
                        data = json.loads(line)

                        time_stamp = data["time"]

                        dataArray = []

                        for item in data["data"]:
                            dataArray.append({"x": item[0], "y": item[1], "t": item[2]})

                        # Append the data to the list
                        xy_time_data.append({"time": time_stamp, "data": dataArray})

                        # Print the received data (optional)
                        print(f"Processed data: time={time_stamp}")

                    except json.JSONDecodeError:
                        print("Failed to decode JSON data from log line")
    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found")
        return

    # Save x/y time data to JSON file
    output_json_path = log_file_path.rsplit('.', 1)[0] + "_processed.json"
    with open(output_json_path, 'w') as json_file:
        json.dump({"data": xy_time_data}, json_file, indent=4)

    print(f"x/y time data saved to '{output_json_path}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log.py <log_file_path>")
    else:
        log_file_path = sys.argv[1]
        process_log_file(log_file_path)