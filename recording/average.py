# open a json file selected by the user
# read the data from the json file
# for each datapoint in data for each of the times in xy_time_data.json file do the following:
# take the average of the x and y and t values and resave it to a new json file named {name}_average.json

import json
import sys

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        with open(arg, 'r') as file:
            xy_time_data = json.load(file)["data"]

        # List to store the average data
        average_data = []

        for data_point in xy_time_data:
            average_x = 0
            average_y = 0
            average_t = 0

            count = 0

            for item in data_point["data"]:
                # remove data that is well out of the field
                if item["x"] < -1.8 or item["x"] > 1.8 or item["y"] < -1.8 or item["y"] > 1.8:
                    continue
                count += 1

                average_x += item["x"] if isinstance(item["x"], (int, float)) else 0
                average_y += item["y"] if isinstance(item["y"], (int, float)) else 0
                average_t += item["t"] if isinstance(item["t"], (int, float)) else 0

            average_x /= count
            average_y /= count
            average_t /= count

            average_data.append({"time": data_point["time"], "data": [{"x": average_x, "y": average_y, "t": average_t}]})

        # Save the average data to a JSON file
        average_file = f"{arg.split('.')[0]}_average.json"
        with open(average_file, 'w') as json_file:
            json.dump({"data": average_data}, json_file, indent=4)

        print(f"Average data saved to '{average_file}'.")