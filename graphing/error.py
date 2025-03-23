import json
import sys
import math
from concurrent.futures.process import ProcessPoolExecutor

import matplotlib.pyplot as plt
import asyncio
from concurrent.futures import ThreadPoolExecutor
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
        if mse < min_mse:
            min_mse = mse
            best_offset = offset

    return best_offset

def plot_error_over_time(time_stamps, errors):
    plt.plot(time_stamps, errors, marker='o')
    plt.xlabel('Time')
    plt.ylabel('Error (Distance)')
    plt.title('Error Over Time')
    plt.grid(True)
    plt.show()

async def main():
    if len(sys.argv) < 3:
        print("Usage: python error.py <file1.json> <file2.json>")
        sys.exit(1)

    file1_path = sys.argv[1]
    file2_path = sys.argv[2]

    data1 = read_json_file(file1_path)
    data2 = read_json_file(file2_path)

    max_offset = 10  # Define the maximum offset to search
    best_offset = await find_best_offset(data1, data2, max_offset)

    time_stamps = []
    errors = []

    for point1 in data1:
        closest_point2 = find_closest_point(point1["time"] + best_offset, data2)
        time_stamps.append(point1["time"])
        error = calculate_distance(point1["data"][0], closest_point2["data"][0])
        errors.append(error)

    plot_error_over_time(time_stamps, errors)

if __name__ == "__main__":
    asyncio.run(main())