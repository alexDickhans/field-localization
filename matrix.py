import json
import numpy as np

# Define a class to represent the data structure
class CoordinateSystem:
    def __init__(self, data):
        # Initialize the origin as a NumPy array
        self.origin = np.array([data["origin"]["x"], data["origin"]["y"]])
        # Initialize the matrix as a NumPy array
        self.matrix = np.array(data["matrix"])

    def inverse(self, input_vector):
        final = self.matrix @ input_vector
        return final + self.origin

    def transform(self, input_vector):
        translated = input_vector - self.origin
        final = np.linalg.inv(self.matrix) @ translated
        return final

    def __repr__(self):
        return f"CoordinateSystem(origin={self.origin}, matrix=\n{self.matrix})"

# Load the JSON data from a file
with open('config.json', 'r') as file:
    data = json.load(file)

coordinate_system = CoordinateSystem(data)

if __name__ == "__main__":

    # Ask user for input vector
    input_vector = np.array([float(input("Enter x: ")), float(input("Enter y: "))])

    # Transform the input vector using the member function
    result = coordinate_system.transform(input_vector)

    print(coordinate_system)

    print(result)
