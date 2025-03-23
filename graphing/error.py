import json
import sys
import math
from concurrent.futures.process import ProcessPoolExecutor

import matplotlib.pyplot as plt
import asyncio
import numpy as np

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)["data"]

def calculate_distance(point1, point2):
    return math.sqrt((point1["x"] - point2["x"])**2 + (point1["y"] - point2["y"])**2)

def find_closest_point(time, data):
    closest_point = min(data, key=lambda x: abs(x["time"] - time))
    return closest_point

def calculate_mse(data1, data2, offset):
    errors = []
    for point1 in data1:
        closest_point2 = find_closest_point(point1["time"] + offset, data2)
        error = calculate_distance(point1["data"][0], closest_point2["data"][0])
        errors.append(error**2)
    mse = sum(errors) / len(errors)
    return mse

async def find_best_offset(data1, data2, max_offset, step=0.05):
    best_offset = 0
    min_mse = float('inf')
    offsets = np.arange(-max_offset, max_offset + step, step)

    with ProcessPoolExecutor(max_workers=14) as executor:  # Specify the number of workers
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, calculate_mse, data1, data2, offset)
            for offset in offsets
        ]
        results = await asyncio.gather(*tasks)

    for offset, mse in zip(offsets, results):
        print(f"Processing offset: {offset}")
        if mse < min_mse:
            min_mse = mse
            best_offset = offset

    return best_offset

def plot_error_over_time(time_stamps, errors, label):
    plt.plot(time_stamps, errors, label=label)

async def main():
    if len(sys.argv) != 4:
        print("Usage: python error.py <ground_truth.json> <file1.json> <file2.json>")
        sys.exit(1)

    ground_truth_path = sys.argv[1]
    file1_path = sys.argv[2]
    file2_path = sys.argv[3]
    max_offset = 10  # Define the maximum offset to search

    ground_truth_data = read_json_file(ground_truth_path)
    file1_data = read_json_file(file1_path)
    file2_data = read_json_file(file2_path)

    for i, (data, label) in enumerate([(file1_data, "Localization"), (file2_data, "Exponential")]):
        print(f"Processing {label}")
        best_offset = await find_best_offset(ground_truth_data, data, max_offset)

        time_stamps = []
        errors = []

        for point in ground_truth_data:
            closest_point = find_closest_point(point["time"] + best_offset, data)
            time_stamps.append(point["time"])
            error = calculate_distance(point["data"][0], closest_point["data"][0])
            errors.append(error)

        plot_error_over_time(time_stamps, errors, label=label)

    plt.xlabel('Time')
    plt.ylabel('Error (Distance)')
    plt.title('Error Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())