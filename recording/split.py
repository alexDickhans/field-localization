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

            loc_data.append(data_point["data"][0])
            des_data.append(data_point["data"][1])

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