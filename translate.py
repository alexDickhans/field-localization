# script to make the config given in the config.json file
# ask user for origin, x and y and construct the matrix accordingly

import json


def get_coordinate_input(prompt):
    while True:
        try:
            x = float(input(f"Enter the x coordinate for {prompt}: "))
            y = float(input(f"Enter the y coordinate for {prompt}: "))
            return {"x": x, "y": y}
        except ValueError:
            print("Invalid input. Please enter numeric values.")


def main():
    origin = get_coordinate_input("origin")
    x_point = get_coordinate_input("x point")
    y_point = get_coordinate_input("y point")

    config = {
        "origin": origin,
        "matrix": [[x_point["x"] - origin["x"], y_point["x"] - origin["x"]],
                   [x_point["y"] - origin["y"], y_point["y"] - origin["y"]]]
    }

    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

    print("Configuration saved to config.json")


if __name__ == "__main__":
    main()
