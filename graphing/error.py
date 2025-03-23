import json
import sys
import math
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import asyncio
import numpy as np

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

    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, calculate_mse, data1, data2, offset) for offset in offsets]
        results = await asyncio.gather(*tasks)

    for offset, mse in zip(offsets, results):
        if mse < min_mse:
            min_mse = mse
            best_offset = offset

    print(f"Best offset: {best_offset}, MSE: {min_mse}")
    return best_offset

def plot_error_over_time(time_stamps, errors, label):
    plt.plot(time_stamps, errors, label=label)

async def main():
    if len(sys.argv) < 4 or len(sys.argv) % 3 != 1:
        print("Usage: python error.py <ground_truth1.json> <data1.json> <data2.json> [<ground_truth2.json> <data3.json> <data4.json> ...]")
        sys.exit(1)

    file_triplets = [(sys.argv[i], sys.argv[i + 1], sys.argv[i + 2]) for i in range(1, len(sys.argv), 3)]
    max_offset = 10  # Define the maximum offset to search

    for i, (ground_truth_path, data1_path, data2_path) in enumerate(file_triplets):
        print(f"Processing triplet {i + 1}: {ground_truth_path}, {data1_path}, {data2_path}")
        ground_truth_data = read_json_file(ground_truth_path)
        data1 = read_json_file(data1_path)
        data2 = read_json_file(data2_path)

        for j, (data, label) in enumerate([(data1, "Localization"), (data2, "Exponential")]):
            print(f"Processing {label} for triplet {i + 1}")
            best_offset = await find_best_offset(ground_truth_data, data, max_offset)

            time_stamps = []
            errors = []

            for point in ground_truth_data:
                closest_point = find_closest_point(point["time"] + best_offset, data)
                time_stamps.append(point["time"])
                error = calculate_distance(point["data"][0], closest_point["data"][0])
                errors.append(error)

            plot_error_over_time(time_stamps, errors, label=f'Trial {i + 1} - {label}')

    plt.xlabel('Time')
    plt.ylabel('Error (Distance in meters)')
    plt.title('Error Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())