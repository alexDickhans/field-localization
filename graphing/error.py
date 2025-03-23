import json
import sys
import math
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import asyncio
import numpy as np
from scipy.signal import savgol_filter
import csv

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)["data"]

def calculate_distance(point1, point2):
    return np.sqrt((point1["x"] - point2["x"])**2 + (point1["y"] - point2["y"])**2)

def find_closest_point(time, data):
    times = np.array([point["time"] for point in data])
    closest_index = np.argmin(np.abs(times - time))
    return data[closest_index]

def calculate_mse(data1, data2, offset):
    errors = []
    for point1 in data1:
        closest_point2 = find_closest_point(point1["time"] + offset, data2)
        error = calculate_distance(point1["data"][0], closest_point2["data"][0])
        errors.append(error**2)
    mse = np.mean(errors)
    return mse

async def find_best_offset(data1, data2, max_offset, step=0.05):
    offsets = np.arange(-max_offset, max_offset + step, step)
    min_mse = float('inf')
    best_offset = 0
    mse_values = []

    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, calculate_mse, data1, data2, offset) for offset in offsets]
        results = await asyncio.gather(*tasks)

    for offset, mse in zip(offsets, results):
        mse_values.append((offset, mse))
        if mse < min_mse:
            min_mse = mse
            best_offset = offset

    print(f"Best offset: {best_offset}, MSE: {min_mse}")
    return best_offset, mse_values

def plot_error_over_time(time_stamps, errors, label, color):
    smoothed_errors = savgol_filter(errors, window_length=40, polyorder=2)
    plt.plot(time_stamps, smoothed_errors, label=label, color=color)

def has_started_moving(data, threshold=0.05):
    initial_position = data[0]["data"][0]
    for point in data:
        if calculate_distance(initial_position, point["data"][0]) > threshold:
            return point["time"] - 0.5
    return None

async def main():
    if len(sys.argv) < 4 or len(sys.argv) % 3 != 1:
        print("Usage: python error.py <ground_truth1.json> <data1.json> <data2.json> [<ground_truth2.json> <data3.json> <data4.json> ...]")
        sys.exit(1)

    file_triplets = [(sys.argv[i], sys.argv[i + 1], sys.argv[i + 2]) for i in range(1, len(sys.argv), 3)]
    max_offset = 10  # Define the maximum offset to search

    colors = plt.get_cmap('tab10').colors
    optimal_mse_values = []

    for i, (ground_truth_path, data1_path, data2_path) in enumerate(file_triplets):
        print(f"Processing triplet {i + 1}: {ground_truth_path}, {data1_path}, {data2_path}")
        ground_truth_data = read_json_file(ground_truth_path)
        data1 = read_json_file(data1_path)
        data2 = read_json_file(data2_path)

        for j, (data, label, color) in enumerate([(data1, "Localization", colors[0]), (data2, "Exponential", colors[1])]):
            print(f"Processing {label} for triplet {i + 1}")
            best_offset, mse_values = await find_best_offset(ground_truth_data, data, max_offset)

            # Print MSE values in CSV-like format
            print(f"Offset,MSE ({label} - Trial {i + 1})")
            for offset, mse in mse_values:
                print(f"{offset},{mse}")

            optimal_mse_values.append((f'Trial {i + 1} - {label}', best_offset, min(mse_values, key=lambda x: x[1])[1]))

            start_time = has_started_moving(ground_truth_data)
            if start_time is None:
                print(f"Robot did not start moving in {ground_truth_path}")
                continue

            time_stamps = []
            errors = []

            for point in ground_truth_data:
                if point["time"] < start_time:
                    continue
                closest_point = find_closest_point(point["time"] + best_offset, data)
                time_stamps.append(point["time"] - start_time)
                error = calculate_distance(point["data"][0], closest_point["data"][0])
                errors.append(error)

            plot_error_over_time(time_stamps, errors, label=f'Trial {i + 1} - {label}', color=color)

    # Save optimal MSE values to a CSV file
    with open('optimal_mse_values.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Trial', 'Best Offset', 'Optimal MSE'])
        csvwriter.writerows(optimal_mse_values)

    plt.xlabel('Time')
    plt.ylabel('Error (Distance in meters)')
    plt.title('Error Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())