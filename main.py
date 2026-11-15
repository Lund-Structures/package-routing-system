# Routing program. Developed by: Kyle Lund.

import csv
import gui3
from trucks import Truck
from routing_logic import clarke_wright
from direct_map import DirectMap
from datetime import time


# Returns a Direct Map of all package data in 'packagefile.csv'
def load_package_data(csv_file):
    with open(csv_file, newline='') as file:
        # Create Hash table to hold package data
        number_of_packages = sum(1 for row in file if row.strip()) - 8  # Skips header in csv file
        package_data = DirectMap(number_of_packages)

        # Read package data file and create package objects
        file.seek(0)
        reader = csv.reader(file)
        for row in reader:
            try:
                package_id = int(row[0])  # Try to convert first value to int
                package_data.insert(package_id,
                                    address=row[1],
                                    city=row[2],
                                    state=row[3],
                                    zip_code=int(row[4]),
                                    deadline=row[5],
                                    weight=int(row[6]),
                                    note=row[7],
                                    )
            except ValueError:
                continue
        return package_data


# Reads in 'addressCVS' returning dictionary of hub numbers with addresses and names
def load_hubs(csv_file):
    hubs = {}
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                hubs[int(row[0])] = row[2]
            except IndexError:
                continue
    return hubs


# Reads in 'distancetable.csv' and returns a full 2D distance matrix
def load_distance_matrix(csv_file):
    distance_matrix = []

    with open(csv_file, newline='') as file:
        reader = csv.reader(file)

        for row in reader:
            new_row = []
            valid_cell = False  # Flag to check if the row is a number

            for col in row:
                try:
                    value = float(col)
                    new_row.append(value)
                    valid_cell = True
                except ValueError:
                    continue  # skip non-numeric cells in this row

            # Only add rows that actually had numbers
            if valid_cell:
                distance_matrix.append(new_row)

    # Fill upper triangle from lower triangle
    n = len(distance_matrix)
    for i in range(n):
        for j in range(i + 1, n):
            distance_matrix[i].append(distance_matrix[j][i])

    return distance_matrix


# Returns a list of hub numbers given a package list
def get_hub_indices(package_list, data, hubs):
    hub_indices = []  # Holds the hub numbers for each package, duplicate hub numbers may exist
    clean_list = []  # Holds a sorted list of hub numbers, no duplicates
    for package in package_list:
        address = data.get_address(int(package))
        for key, value in hubs.items():
            if address and value in address:
                hub_indices.append(int(key))
    for item in hub_indices:
        if item not in clean_list:
            clean_list.append(item)
    clean_list.sort()
    return clean_list


def main():
    # Import delivery and distance data from csv files
    packages_data = load_package_data('packagefile.csv')  # Imports package data and directly maps it to a hash table
    list_matrix = load_distance_matrix('distancetable.csv')  # Imports distance matrix from csv file to a 2D list
    hubs = load_hubs('address.csv')  # Imports hub numbers and hub names to a dictionary

    # Assign packages to each truck

    truck1_load = [1, 13, 14, 15, 16, 19, 20, 30, 31, 34, 37, 39, 40]
    truck2_load = [3, 6, 12, 18, 22, 24, 25, 26, 28, 29, 32, 36, 38]
    truck3_load = [2, 4, 5, 7, 8, 9, 10, 11, 17, 21, 23, 27, 33, 35]
    urgent_orders = [15, 25, 29]  # Add priority orders to urgent_orders list
    cargo = [truck1_load, truck2_load, truck3_load]

    # Truck 1
    # Find truck stops -> build efficient route -> Load packages onto truck ->
    # -> Mutate truck route to prioritize urgent orders
    truck1_stops = get_hub_indices(truck1_load, packages_data, hubs)
    truck1_route = clarke_wright(list_matrix, truck1_stops)
    truck1 = Truck(list_matrix, truck1_route)
    truck1.set_hub_list(hubs)
    truck1.load_packages(truck1_load)
    truck1.package_data_reference(packages_data)
    truck1.handle_urgent_orders(urgent_orders)

    # Truck 2
    # Find truck stops -> build efficient route -> Load packages onto truck ->
    # -> Mutate truck route to prioritize urgent orders -> Delay truck until all its packages arrive at depot @ 09:05
    truck2_stops = get_hub_indices(truck2_load, packages_data, hubs)
    truck2_route = clarke_wright(list_matrix, truck2_stops)
    truck2 = Truck(list_matrix, truck2_route)
    truck2.set_hub_list(hubs)
    truck2.load_packages(truck2_load)
    truck2.package_data_reference(packages_data)
    truck2.handle_urgent_orders(urgent_orders)
    truck2.set_start_time(time(9, 5))

    # Truck 3
    # Find truck stops -> build efficient route -> Load packages onto truck ->
    # -> Mutate truck route to prioritize urgent orders -> Wait at depot until a driver becomes available
    truck3_stops = get_hub_indices(truck3_load, packages_data, hubs)
    truck3_route = clarke_wright(list_matrix, truck3_stops)
    truck3 = Truck(list_matrix, truck3_route)
    truck3.set_hub_list(hubs)
    truck3.load_packages(truck3_load)
    truck3.package_data_reference(packages_data)
    truck3.handle_urgent_orders(urgent_orders)

    # Create a list of all delivery trucks
    truck_list = [truck1, truck2, truck3]

    # Simulate Deliveries
    minutes_in_workday = 540  # 08:00 - 17:00(5:00PM) The number of minutes in a typical work day
    available_driver = False
    while minutes_in_workday > 0:
        truck1.move(1)
        if minutes_in_workday <= 475:  # Truck2 Leaves Depot At 09:05 AM
            truck2.move(1)
        if minutes_in_workday == 400:  # Update package 9 with correct address at 10:20 AM
            packages_data.table[9][1] = "410 S State St"
            packages_data.table[9][2] = "Salt Lake City"
            packages_data.table[9][3] = "UT"
            packages_data.table[9][4] = "84111"
            packages_data.table[9][7] = "Correct Address Updated"

        # Deploy Truck 3 after Truck 1 returns to hub
        if not truck1.cargo and truck1.route[truck1.current_hub_index] == 0 and available_driver is False:
            available_driver = True
            truck3.set_start_time(truck1.end_time)
        if available_driver is True:
            truck3.move(1)
        # The day ends when all packages are delivered or there is no more time in the work day
        if not truck1.cargo and not truck2.cargo and not truck3.cargo:
            print("All Packages Have Been Delivered")
            break
        minutes_in_workday -= 1

    # Print accumulative travel distance of all trucks. accumulative-distance < 140 miles
    print(
        f"Total Distance Traveled From All trucks: {round(truck1.total_mileage + truck2.total_mileage + truck3.total_mileage)}")

    # Launch GUI
    model = gui3.Model(packages_data, truck_list, cargo)
    controller = gui3.Controller(model)
    app = gui3.MainWindow(controller)
    app.mainloop()


if __name__ == '__main__':
    main()
