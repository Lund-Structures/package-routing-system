import copy
import datetime
from datetime import datetime, timedelta, time
import routing_logic
from routing_logic import clarke_wright
from direct_map import DirectMap


# The Truck class creates Truck objects that hold a list of package ID's.
# Trucks have several data members such as speed, start time, and route that all help in delivering packages on a route
class Truck:
    def __init__(self, route_matrix, route, speed=18):
        self.cargo = []  # Package ID's associated with a truck. len(cargo) < 17
        self.start_time = time(8, 0)  # 08:00 AM
        self.end_time = None
        self.route_matrix = route_matrix  # Distance matrix between all hubs
        self.route = route  # list of hub IDs to visit
        self.speed = speed / 60.0  # miles per minute
        self.total_mileage = 0.0
        self.current_leg_distance = 0.0
        self.current_hub_index = 0
        self.current_position = "Depot"
        self.hub_names = {}
        self.package_data = DirectMap
        self.package_data_copy = []
        self.next_hub_threshold = None

    # Moves the truck along it's route given a number of minutes
    def move(self, minutes):
        time_remaining = minutes

        # Keep track of the next "goal mileage" for the current hub
        if getattr(self, "next_hub_threshold", None) is None:
            self.next_hub_threshold = self.total_mileage + self.route_matrix[self.route[self.current_hub_index]][
                self.route[self.current_hub_index + 1]]

        # While there is still time left and the truck hasn't returned to the depot move the truck along its route
        while time_remaining > 0 and self.current_hub_index < len(self.route) - 1:
            time_remaining -= 1
            self.total_mileage += self.speed * 1

            if self.total_mileage < self.next_hub_threshold:
                # Still on the road
                self.current_position = f"En route to {self.hub_names.get(self.route[self.current_hub_index + 1], 'Off the grid!!!!')}"
                continue
            else:
                # Truck arrives at hub
                self.current_hub_index += 1
                self.deliver_packages(self.route[self.current_hub_index])  # Deliver packages to hub
                if self.stale_package_data():  # Check for stale data in Hash Table, update route/package data if stale
                    self.package_data_reference(self.package_data)
                    self.update_route()

                self.current_position = f"Arrived at {self.hub_names.get(self.route[self.current_hub_index], 'Off the grid!!!!')}"

                # Set new threshold for the next hub (if any)
                if self.current_hub_index < len(self.route) - 1:
                    next_hub = self.route[self.current_hub_index + 1]
                    prev_hub = self.route[self.current_hub_index]
                    self.next_hub_threshold = self.total_mileage + self.route_matrix[prev_hub][next_hub]
        self.end_time = self.get_timestamp()

    # Loads a single package to Trucks cargo
    def load_package(self, package_id):
        self.cargo.append(package_id)

    # Loads a list of packages to Trucks cargo
    def load_packages(self, package_list):
        self.cargo.extend(package_list)

    # References hub names for Truck class access
    def set_hub_list(self, all_hub_list):
        self.hub_names = all_hub_list

    # Sets a start time for truck deliveries
    def set_start_time(self, new_time):
        self.start_time = new_time

    # References full hub distance matrix for truck use
    def set_matrix(self, sub_matrix):
        self.route_matrix = sub_matrix

    # "Delivers" or removes all packages in cargo associated with a delivery address
    def deliver_packages(self, hub_id):
        hub_name = self.hub_names[hub_id]
        delivery_time = self.get_timestamp()
        for package in self.cargo[:]:
            if self.package_address(package) in hub_name:
                self.package_data.update(package, f'Package Delivered @ {delivery_time}')
                self.cargo.remove(package)
            else:
                continue

    # References all package data for truck use
    def package_data_reference(self, package_data):
        self.package_data = package_data
        self.package_data_copy = copy.deepcopy(self.package_data.table)

    # Returns the street address of a package given its ID
    def package_address(self, package_id):
        address = self.package_data.lookup(package_id)[0]
        return address

    # Prints all package IDs associated with a truck. Used for debugging only
    def honk(self):
        print(self.cargo)

    # Returns a time stamp based on a trucks start time and distance traveled
    def get_timestamp(self):
        minutes_elapsed = (self.total_mileage / self.speed)
        start_time = datetime.combine(datetime.today(), self.start_time)
        end_time = start_time + timedelta(minutes=minutes_elapsed)
        return end_time.time()

    # Checks for stale data against DirectMap(all packages)
    def stale_package_data(self):
        for package in self.cargo:
            address = self.package_address(package)
            if address is not self.package_data_copy[package][1]:
                return True  # Stale Address Data found
        return False  # No stale Data found

    # Rebuilds Truck route if stale data is found.
    # New routes first entry is whichever hub the truck visited last.
    # Routes should update only after a truck has reached a hub
    def update_route(self):
        hub_indicies = []
        clean_list = []
        for package in self.cargo:
            address = self.package_address(package)
            for key, value in self.hub_names.items():
                if address and value in address:
                    hub_indicies.append(int(key))
        for item in hub_indicies:
            if item not in clean_list:
                clean_list.append(item)
        clean_list.sort()
        new_route = routing_logic.clarke_wright(self.route_matrix, clean_list)
        new_route[0] = self.route[self.current_hub_index]
        self.current_hub_index = 0
        self.route = new_route

    # Rebuilds route prioritizing select package IDs
    def handle_urgent_orders(self, urgent_orders):
        urgent_route = []  # Holds hub IDs for prioritized packages, may have duplicate hub IDs
        final_route = []  # Holds efficient route path for urgent packages, no duplicate hub IDs
        for package in urgent_orders:
            if package in self.cargo:
                hub_address = self.package_address(package)
                for hub_key, hub_value in self.hub_names.items():
                    if hub_address in hub_value:
                        urgent_route.append(hub_key)
        if len(urgent_route) >= 3:
            cw = clarke_wright(self.route_matrix, urgent_route)  # clarke wright algorithm is used to build sub-route
            for i in reversed(cw[1:]):
                self.route.insert(1, i)  # Insert urgent sub-route into front of full route
            for i in self.route:
                if i not in final_route:
                    final_route.append(i)
            self.route = final_route
            self.route.append(0)
        else:
            for i in urgent_route:
                self.route.insert(1, i)
            for i in self.route:
                if i not in final_route:
                    final_route.append(i)
            self.route = final_route
            self.route.append(0)
        return final_route
