import json
import sys


# Function to process the log file and save it to a JSON file
def process_log_file(log_file_path):
    # List to store x/y time data

    try:
        with open(log_file_path, 'r') as log_file:
            # Lists to store localization and desired data
            localization_data = []
            localization_average = []
            desired_data = []

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
                        localization_data.append({"time": time_stamp, "data": dataArray[0:-1]})
                        desired_data.append({"time": time_stamp, "data": [dataArray[-1]]})

                        # Find the average x, y, t for the localization data
                        x_sum = 0
                        y_sum = 0
                        t_sum = 0

                        for item in dataArray[0:-1]:
                            x_sum += item["x"]
                            y_sum += item["y"]
                            t_sum += item["t"]

                        x_avg = x_sum / len(dataArray[0:-1])
                        y_avg = y_sum / len(dataArray[0:-1])
                        t_avg = t_sum / len(dataArray[0:-1])

                        localization_average.append({"time": time_stamp, "data": [{"x": x_avg, "y": y_avg, "t": t_avg}]})

                        # Print the received data (optional)
                        print(f"Processed data: time={time_stamp}")

                    except json.JSONDecodeError:
                        print("Failed to decode JSON data from log line")

            # Save the localization data to a JSON file
            localization_file = f"{sys.argv[1].split('.')[0]}_localization.json"
            with open(localization_file, 'w') as json_file:
                json.dump({"data": localization_data}, json_file, indent=4)

            # Save the desired data to a JSON file
            desired_file = f"{sys.argv[1].split('.')[0]}_desired.json"
            with open(desired_file, 'w') as json_file:
                json.dump({"data": desired_data}, json_file, indent=4)

            # Save the localization average data to a JSON file
            localization_average_file = f"{sys.argv[1].split('.')[0]}_localization_average.json"
            with open(localization_average_file, 'w') as json_file:
                json.dump({"data": localization_average}, json_file, indent=4)

            print(f"Localization data saved to '{localization_file}'.")
            print(f"Desired data saved to '{desired_file}'.")
            print(f"Localization average data saved to '{localization_average_file}'.")

    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found")
        return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log.py <log_file_path>")
    else:
        log_file_path = sys.argv[1]
        process_log_file(log_file_path)