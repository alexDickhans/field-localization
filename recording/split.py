import json
import sys

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        with open(arg, 'r') as file:
            xy_time_data = json.load(file)["data"]

        # Lists to store localization and desired data
        localization_data = []
        desired_data = []

        for data_point in xy_time_data:
            loc_data = []
            des_data = []

            for item in data_point["data"]:
                if item["t"] is None:
                    loc_data.append({"x": item["x"], "y": item["y"]})
                else:
                    des_data.append({"x": item["x"], "y": item["y"], "t": item["t"]})

            localization_data.append({"time": data_point["time"], "data": loc_data})
            desired_data.append({"time": data_point["time"], "data": des_data})

        # Save the localization data to a JSON file
        localization_file = f"{arg.split('.')[0]}_localization.json"
        with open(localization_file, 'w') as json_file:
            json.dump({"data": localization_data}, json_file, indent=4)

        # Save the desired data to a JSON file
        desired_file = f"{arg.split('.')[0]}_desired.json"
        with open(desired_file, 'w') as json_file:
            json.dump({"data": desired_data}, json_file, indent=4)

        print(f"Localization data saved to '{localization_file}'.")
        print(f"Desired data saved to '{desired_file}'.")