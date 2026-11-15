# Direct Map class holds all package data in a hash table. The Direct Map index correlates directly to the package ID
class DirectMap:
    def __init__(self, size):
        self.table = [None] * size  # Builds package table given number of packages

    # Inserts package data as a list into self.table
    def insert(self, package_id, address, city, state, zip_code, deadline, weight, note):
        self.table[package_id] = [
            package_id,  # [0]
            address,     # [1]
            city,        # [2]
            state,       # [3]
            zip_code,    # [4]
            deadline,    # [5]
            weight,      # [6]
            note,        # [7]
            "Processing Package at Depot"  # [8]
        ]

    # Returns select package data given package id. Returns None of id not found
    def lookup(self, package_id):
        if isinstance(package_id, int) and self.table[package_id] is not None and (len(self.table) >= package_id):
            package = self.table[package_id]
            return package[1], package[2], package[4], package[5], package[6], package[8]
            #      Address  |    City   |  Zip Code |  Deadline |  Weight   |  Status
        return None  # Return none if package id not found

    # Updates the package status, prints error message if package ID not found
    def update(self, pkg_id, status):
        if pkg_id is not None:
            pkg_id = int(pkg_id)
            self.table[pkg_id][8] = str(status)
        else:
            print("Unable to update package, package ID not found")

    # Returns the street address of a package given it's ID. Returns None if ID not found
    def get_address(self, package_id):
        try:
            # Ensure package_id is within bounds
            if 0 <= package_id < len(self.table):
                package = self.table[package_id]
                if package is not None:
                    return package[1]  # return address
        except (IndexError, TypeError) as e:
            # Handle invalid index or bad data
            print(f"Error getting address for package {package_id}: {e}")
        return None  # return None if not found
