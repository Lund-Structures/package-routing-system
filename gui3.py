import tkinter as tk
from datetime import datetime, time, timedelta


# Model View Controller Structure
# Model holds all the important data needed to populate the GUI
class Model:
    def __init__(self, package_data, truck_list, truck_cargo):
        self.packages_data = package_data
        self.truck_list = truck_list
        self.truck_cargo = truck_cargo


# Controller class bridges the communication between the view and the model
class Controller:
    def __init__(self, model):
        self.model = model

    def get_all_packages(self):
        return self.model.packages_data

    def lookup_package(self, package):
        package_id = package
        return self.model.packages_data.lookup(package_id)

    def get_all_cargo(self, truck_number):
        return self.model.truck_cargo

    def get_truck(self, truck_number):
        return self.model.truck_list[truck_number - 1]

    def package_status(self, package_id):
        return self.model.packages_data.lookup(package_id)[5]

    def package_deadline(self, package_id):
        return self.model.packages_data.lookup(package_id)[3]

    def route_status(self, truck_number, user_time):
        truck = self.get_truck(truck_number)
        cargo = self.get_all_cargo(truck_number)[truck_number - 1]
        low_time = time(0, 0)  # earliest possible
        high_time = time(23, 59, 59)  # latest possible
        last_stop = None
        next_stop = None

        for package in cargo:
            try:
                delivered_time = self.package_status(package)
                delivered_time = datetime.strptime(delivered_time.split("@")[1].strip(), "%H:%M:%S").time()

                if delivered_time <= user_time:
                    if delivered_time > low_time:
                        low_time = delivered_time
                        last_stop = truck.package_address(package)

                if delivered_time >= user_time:
                    if delivered_time < high_time:
                        high_time = delivered_time
                        next_stop = truck.package_address(package)
            except IndexError:
                continue
        # --- handle edge cases ---
        if next_stop is None or user_time < truck.start_time:
            # user_time is after last delivery → truck returned to hub
            next_stop = "Depot"
        if isinstance(truck.end_time, timedelta):
            total_seconds = truck.end_time.total_seconds()
            hours = int(total_seconds // 3600) % 24
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            end_time = time(hours, minutes, seconds)
        else:
            end_time = time(0, 0)

        if last_stop is None or user_time > end_time:
            # user_time is before first delivery → truck still at hub
            last_stop = "Depot"

        return [last_stop, next_stop]


# Main window contains the main menu, no package data is shown in this window
class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("WGUPS")
        self.geometry("900x300")
        self.resizable(False, False)

        # Configure 3 columns and rows
        for col in range(3):
            self.columnconfigure(col, weight=1)
        for row in range(3):
            self.rowconfigure(row, weight=1)

        # Title Label
        tk.Label(
            self,
            text="Main Menu",
            font=("Arial", 18, "bold"),
            fg="#001731"
        ).grid(row=0, column=1)

        # Package Lookup Button
        tk.Button(
            self,
            text="Package Lookup",
            font=("Arial", 12, "bold"),
            width=18,
            height=8,
            bg="#0474f4",
            fg="white",
            activebackground="#001731",
            activeforeground="white",
            command=self.open_lookup_window
        ).grid(row=1, column=0)

        # Trucks Button
        tk.Button(
            self,
            text="Trucks",
            font=("Arial", 12, "bold"),
            width=18,
            height=8,
            bg="#0474f4",
            fg="white",
            activebackground="#001731",
            activeforeground="white",
            command=self.open_trucks_window
        ).grid(row=1, column=1)

        # Delivery Status Button
        tk.Button(
            self,
            text="Delivery Status",
            font=("Arial", 12, "bold"),
            width=18,
            height=8,
            bg="#0474f4",
            fg="white",
            activebackground="#001731",
            activeforeground="white",
            command=self.open_delivery_window
        ).grid(row=1, column=2)

    def open_lookup_window(self):
        LookupWindow(self.controller)

    def open_trucks_window(self):
        TrucksWindow(self.controller)

    def open_delivery_window(self):
        DeliveryWindow(self.controller)


# Lookup Window allows users to view all package information given a package ID
class LookupWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Package Lookup")
        self.geometry("550x450")
        self.resizable(False, False)

        # Configure 3 columns and 10 rows
        for col in range(3):
            self.columnconfigure(col, weight=1)
        for row in range(10):
            self.rowconfigure(row, weight=1)

        # Header title
        tk.Label(self,
                 text="Lookup Package By ID:",
                 font=("Arial", 18, "bold"),
                 ).grid(row=0, column=1)

        # SpinBox for package lookup, only accepts integers 0-100
        self.id_spinner = tk.Spinbox(self,
                                     width=3,
                                     from_=0, to=100,
                                     command=lambda: self.display_package(int(self.id_spinner.get()))
                                     )
        self.id_spinner.grid(row=2, column=1)

        # Lookup button fetches and displays package data to gui
        tk.Button(self,
                  text="Lookup Package",
                  command=lambda: self.display_package(self.id_spinner.get()) if self.id_spinner.get().isdigit() else print("Invalid input. ONLY NUMERIC INPUT ACCEPTED")
                  # (if self.display_package(self.id_spinner.get()).isdigit())
                  ).grid(row=2, column=3)

        # Delivery Address Label
        tk.Label(self,
                 text="Delivery Address:",
                 font=("Arial", 12, "bold"),
                 ).grid(row=3, column=0, pady=10)

        self.address_label = tk.Label(self,
                                      text="N/A",
                                      font=("Arial", 12))
        self.address_label.grid(row=3, column=1, pady=10)

        # Delivery Deadline Label
        tk.Label(self,
                 text=" Delivery Deadline:",
                 font=("Arial", 12, "bold"),
                 ).grid(row=4, column=0, pady=10)

        self.deadline_label = tk.Label(self,
                                       text="N/A",
                                       font=("Arial", 12))
        self.deadline_label.grid(row=4, column=1, pady=10)

        # Delivery city Label
        tk.Label(self,
                 text=" Delivery City         :",
                 font=("Arial", 12, "bold"),
                 ).grid(row=5, column=0, pady=10)

        self.city_label = tk.Label(self,
                                   text="N/A",
                                   font=("Arial", 12))
        self.city_label.grid(row=5, column=1, pady=10)

        # Delivery zip code label
        tk.Label(self,
                 text="Delivery Zip Code:",
                 font=("Arial", 12, "bold"),
                 ).grid(row=6, column=0, pady=10)

        self.zipcode_label = tk.Label(self,
                                      text="N/A",
                                      font=("Arial", 12))
        self.zipcode_label.grid(row=6, column=1, pady=10)

        # Package weight label
        tk.Label(self,
                 text="Package Weight   :",
                 font=("Arial", 12, "bold"),
                 ).grid(row=7, column=0, pady=10)

        self.weight_label = tk.Label(self,
                                     text="N/A",
                                     font=("Arial", 12))
        self.weight_label.grid(row=7, column=1, pady=10)

        # Delivery status label
        tk.Label(self,
                 text="Delivery Status    :",
                 font=("Arial", 12, "bold"),
                 ).grid(row=8, column=0, pady=10)

        self.status_label = tk.Label(self,
                                     text="N/A",
                                     font=("Arial", 12))
        self.status_label.grid(row=8, column=1, pady=10)

    # Displays package data given package ID
    def display_package(self, package_id):

        try:
            result = int(package_id)  # Validate user input is numeric
            result = self.controller.lookup_package(package_id)

            if result is not None:  # Set labels reflecting package data
                self.address_label.config(text=result[0], fg="black")
                self.deadline_label.config(text=result[3], fg="black")
                self.city_label.config(text=result[1], fg="black")
                self.zipcode_label.config(text=result[2], fg="black")
                self.weight_label.config(text=result[4], fg="black")
                self.status_label.config(text=result[5], fg="black")
            else:  # Set error labels
                self.address_label.config(text=f"No Package with ID: {package_id}", fg="red")
                self.deadline_label.config(text="*", fg="red")
                self.city_label.config(text="*", fg="red")
                self.zipcode_label.config(text="*", fg="red")
                self.weight_label.config(text="*", fg="red")
                self.status_label.config(text="*", fg="red")
        except ValueError:
            self.address_label.config(text="Invalid package ID.", fg="red")


# Truck Window offers selection of a specific truck, no package or truck data is shown in this window
class TrucksWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Trucks")
        self.geometry("600x300")
        self.resizable(False, False)

        # Truck ASCII art to display on buttons
        truck1 = [
            "   ________",
            "  |  ____  |___",
            "  | |  1 | |   \\",
            "  |_|____|_|____|",
            "   O        O"
        ]

        truck2 = [
            "   ________",
            "  |  ____  |___",
            "  | |  2 | |   \\",
            "  |_|____|_|____|",
            "   O        O"
        ]

        truck3 = [
            "   ________",
            "  |  ____  |___",
            "  | |  3 | |   \\",
            "  |_|____|_|____|",
            "   O        O"
        ]

        # Join with newline characters
        truck_art1 = "\n".join(truck1)
        truck_art2 = "\n".join(truck2)
        truck_art3 = "\n".join(truck3)

        # Configure 3 columns and 2 rows
        for col in range(3):
            self.columnconfigure(col, weight=1)
        for row in range(2):
            self.rowconfigure(row, weight=1)

        # Truck 1 button
        truck1 = tk.Button(self,
                           text=truck_art1,
                           font=("Courier", 10),
                           width=20, height=6,
                           bg="#0474f4",
                           fg="white",
                           activebackground="#001731",
                           activeforeground="white",
                           justify="left",
                           command=lambda: self.open_truck_tracker(1)
                           )
        truck1.grid(row=1, column=0)

        # Truck 2 button
        truck2 = tk.Button(self,
                           text=truck_art2,
                           font=("Courier", 10),
                           width=20, height=6,
                           bg="#0474f4",
                           fg="white",
                           activebackground="#001731",
                           activeforeground="white",
                           justify="left",
                           command=lambda: self.open_truck_tracker(2)
                           )
        truck2.grid(row=1, column=1)

        # Truck 3 button
        truck3 = tk.Button(self,
                           text=truck_art3,
                           font=("Courier", 10),
                           width=20, height=6,
                           bg="#0474f4",
                           fg="white",
                           activebackground="#001731",
                           activeforeground="white",
                           justify="left",
                           command=lambda: self.open_truck_tracker(3)
                           )
        truck3.grid(row=1, column=2)

        # Header Label
        tk.Label(self,
                 text="Delivery Trucks",
                 font=("Arial", 18, "bold"),
                 fg="#001731"
                 ).grid(row=0, column=1)

        # Truck 1 button label
        tk.Label(self,
                 text="Truck 1",
                 font=("Arial", 12, "bold"),
                 ).grid(row=2, column=0)

        # Truck 2 button label
        tk.Label(self,
                 text="Truck 2",
                 font=("Arial", 12, "bold"),
                 ).grid(row=2, column=1)

        # Truck 3 button label
        tk.Label(self,
                 text="Truck 3",
                 font=("Arial", 12, "bold"),
                 ).grid(row=2, column=2)

    def open_truck_tracker(self, truck_number):
        TruckTracker(self.controller, truck_number)


# Truck Tracker window displays important data from trucks and packages associated with a truck.
class TruckTracker(tk.Toplevel):
    def __init__(self, controller, truck_number):
        super().__init__()
        self.controller = controller
        self.truck = self.controller.get_truck(int(truck_number))
        self.all_cargo = self.controller.get_all_cargo(int(truck_number))
        self.title("Truck Tracker")
        self.geometry("600x800")
        self.resizable(False, False)
        self.labels = {}
        self.truck_number = truck_number
        self.mileage = 0

        # Header label
        tk.Label(self, text="Truck & Package status", font=("Arial", 18, "bold"), pady=10).grid(row=0, column=1)

        # Truck ASCII art for window graphics.
        truck1 = [
            " ________",
            "|  ____  |___",
            f"| |  {truck_number} | |   \\",
            "|_|____|_|____|",
            " O        O"
        ]
        truck_art = "\n".join(truck1)  # Join with newlines

        # Truck frame to hold truck ASCII art
        truck_frame = tk.Frame(self)
        truck_frame.grid(row=1, column=1)
        truck_label = tk.Label(
            truck_frame,
            text=truck_art,
            font=("Courier", 10),
            justify="left"
        )
        truck_label.pack()

        # Label for trucks previous stop
        self.prev_stop = tk.Label(self, text="Previous Hub", font=15)
        self.prev_stop.grid(row=2, column=0, pady=5)

        # Label for trucks current action
        self.mid_lbl = tk.Label(self, text="----En Route To---->", font=15)
        self.mid_lbl.grid(row=2, column=1, pady=5)

        # Label for trucks next destination
        self.next_stop = tk.Label(self, text="Next Hub", font=15)
        self.next_stop.grid(row=2, column=2, pady=5)

        # Mile frame holds labels to display trucks mileage
        mile_frame = tk.Frame(self)
        mile_frame.grid(row=3, column=1, pady=15)
        self.mile_lbl = tk.Label(mile_frame, text="Daily Mileage:", font="bold")
        self.mile_val = tk.Label(mile_frame, text=self.mileage)
        self.mile_lbl.pack(side="left")
        self.mile_val.pack(side="right")

        # Spinner Frame holds labels and spinboxes used to query a truck status given specific time
        spinner_frame = tk.Frame(self)
        spinner_frame.grid(row=4, column=1)

        # Spinbox for clock hours 0-24
        hr_spinner = tk.Spinbox(spinner_frame,
                                width=5,
                                from_=0, to=24,
                                )
        # Spinbox for clock minutes 0-60
        mm_spinner = tk.Spinbox(spinner_frame,
                                width=5,
                                from_=0, to=60,
                                )
        spinner_clue = tk.Label(spinner_frame, text="24hr")
        # Pack elements into spinner frame
        spinner_clue.pack(side="right", pady=0)
        hr_spinner.pack(side="left", pady=0)
        mm_spinner.pack(side="right", pady=0)

        # Button to query truck and package data, collects values from spinbox
        submit_button = tk.Button(self, text="Track Truck",
                                  command=lambda: self.validate_time(hr_spinner.get(), mm_spinner.get())
                                  )
        submit_button.grid(row=4, column=2)

        # Spinbox Labels packed into a frame
        spinner_labels = tk.Frame(self)
        spinner_labels.grid(row=5, column=1)
        hr_lbl = tk.Label(spinner_labels, text=" Hr ", font="bold")
        mm_lbl = tk.Label(spinner_labels, text="mm", font="bold")
        hr_lbl.pack(side="left", pady=0)
        mm_lbl.pack(side="right", pady=0)

        # Column Headers
        tk.Label(self, text="Package ID", font=("Arial", 12, "bold")).grid(row=6, column=0, pady=10)
        tk.Label(self, text="Delivery Due:", font=("Arial", 12, "bold")).grid(row=6, column=1, pady=10)
        tk.Label(self, text="Delivered At:", font=("Arial", 12, "bold")).grid(row=6, column=2, pady=10)

        starting_row = 7  # Start package data table below headers

        # configure 3 columns and as many rows as there are packages on a truck. rows < 16
        for col in range(3):
            self.columnconfigure(col, weight=1)
            for row in range(len(self.all_cargo[truck_number - 1])):
                self.rowconfigure(starting_row + row, weight=1)
                self.lbl = tk.Label(self, text="*", pady=1)
                self.lbl.grid(row=starting_row + row, column=col)
                self.labels[(row, col)] = self.lbl

    # Displays package data given a valid time from spinbox
    def display_cargo(self, hr, mm):
        return_list = []  # Holds package data at a specific time
        user_time = time(int(hr), int(mm))
        # Find the 2 nearest hubs on a  trucks route given a time
        nearest_hubs = self.controller.route_status(self.truck_number, user_time)
        self.display_hubs(nearest_hubs)  # Display 2 nearest hubs and truck position
        try:
            user_time = datetime.strptime(f"{hr}:{mm}", "%H:%M").time()
            if self.truck.start_time < user_time < self.truck.end_time:
                # Convert times into datetime objects with arbitrary dates to allow comparison
                today = datetime.today().date()
                user_dt = datetime.combine(today, user_time)
                start_dt = datetime.combine(today, self.truck.start_time)

                minutes_elapsed = (user_dt - start_dt).seconds / 60
                self.mileage = round(0.3 * minutes_elapsed, 2)
                self.mile_val.config(text=self.mileage)
            elif user_time > self.truck.end_time:
                cute_mi = round(self.truck.total_mileage, 2)
                self.mile_val.config(text=cute_mi)

            for package in self.all_cargo[self.truck_number - 1]:
                delivery_time = self.controller.package_status(package)
                if "@" in delivery_time:
                    delivery_time = datetime.strptime(delivery_time.split("@")[1].strip(), "%H:%M:%S").time()
                    if user_time < self.truck.start_time:
                        # Before start time
                        if package in (6, 25, 28, 32):  # Suggested change came from course community post by Amy Antonucci on Aug 26, 2025
                            return_list.append([package, "DELAYED"])
                        else:
                            return_list.append([package, "At The Main Depot"])
                    elif user_time < delivery_time or isinstance(user_time, str):
                        # after start time
                        return_list.append([package, "En Route"])
                    elif user_time >= self.truck.start_time:
                        return_list.append([package, delivery_time])
                else:
                    return_list.append([package, "En Route"])
            # configure 3 columns and as many rows as there are packages on a truck. rows < 16
            for col in range(3):
                for row in range(len(self.all_cargo[self.truck_number - 1])):
                    package_id = int(return_list[row][0])
                    due_time = self.controller.package_deadline(package_id)
                    status = return_list[row][1]
                    self.labels[(row, 0)].config(text=package_id)
                    self.labels[(row, 1)].config(text=due_time)
                    self.labels[(row, 2)].config(text=status)
        except TypeError:
            # No data displayed if trucks haven't been sent out for deliveries
            print("Trucks have not been told to move yet")

    # Changes labels to reflect trucks current position
    def display_hubs(self, nearest_hubs):
        if nearest_hubs[0] == nearest_hubs[1]:
            self.mid_lbl.config(text="----At Hub---->")
        else:
            self.mid_lbl.config(text="----En Route To---->")
        self.prev_stop.config(text=str(nearest_hubs[0]))
        self.next_stop.config(text=str(nearest_hubs[1]))

    # Validates users input time.
    def validate_time(self, hr, mm):
        try:
            hour = int(hr)
            minute = int(mm)
            if (0 <= hour <= 23) and (0 <= minute <= 59):
                self.display_cargo(hour, minute)
            else:
                print("Input Error:\nEntered Hours must be between 0-23\nEntered Minutes must be between 0-59")
                print(f'You entered:\nHour: {hr}  |  Minute {mm}')
        except ValueError:
            print("Input Error:\nEntered Hours must be between 0-23\nEntered Minutes must be between 0-59")
            print(f'You entered:\nHour: {hr}  |  Minute {mm}')


# Delivery Window displays all packages and their data
class DeliveryWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.time_frame = tk.Frame(self)
        self.column_header_frame = tk.Frame
        self.title("Delivery Status")
        self.geometry("1100x1100")
        self.resizable(False, False)
        self.labels = {}  # Holds all labels for package data
        self.package_data = self.controller.get_all_packages()

        self.build_page()

    def build_page(self):
        # Header Label
        tk.Label(
            self,
            text="All Package Information",
            font=("Arial", 14, "bold"),
            pady=10
        ).grid(row=0, column=0, columnspan=9, sticky="n")

        # Frame for spinbox and it's labels
        self.time_frame.grid(row=1, column=6, columnspan=1)
        time_lbl = tk.Label(self.time_frame, text="Hour (0-24):   ")
        clock_lbl = tk.Label(self.time_frame, text=" O'clock  ")
        hr_spinbox = tk.Spinbox(self.time_frame, width=3,
                                from_=0, to=24, )

        time_lbl.pack(side="left")
        hr_spinbox.pack(side="left")
        clock_lbl.pack(side="left")

        # Update button retrieves and displays package data given a users input time
        update_button = tk.Button(self, text="Update",
                                  command=lambda: self.validate_hour(hr_spinbox.get()))
        update_button.grid(row=1, column=8)

        # spacer row
        tk.Label(self, text="").grid(row=2, column=0)

        # Display the package grid starting after header labels
        self.show_packages_table(start_row=3)

    # Builds the package grid
    def show_packages_table(self, start_row=0):
        # Builds a long list of repetive truck numbers.
        # associated_truck[0] will return the truck number of package_ID = 1
        cargo = self.controller.get_all_cargo(0)
        associated_truck = []
        for package in self.package_data.table:
            if package is None:
                continue
            if package[0] in cargo[0]:
                associated_truck.append(1)
            elif package[0] in cargo[1]:
                associated_truck.append(2)
            elif package[0] in cargo[2]:
                associated_truck.append(3)

        # Column Header Names
        headers = [
            "ID", "Address", "City", "State", "Zip",
            "Deadline",  "Weight", "Note", "Status", " Truck # "
        ]

        # Initialize Column headers
        for col, header in enumerate(headers):
            tk.Label(
                self,
                text=header,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=3
            ).grid(row=start_row, column=col, sticky="nsew")

        # Package Data rows
        row_index = start_row + 1
        truck_lbl_index = 0
        for package in self.package_data.table:
            if package is None:
                continue

            for col, value in enumerate(package):
                # Package data labels
                lbl = tk.Label(
                    self,
                    text=value,
                    borderwidth=1,
                    relief="solid",
                    padx=5,
                    pady=3
                )
                lbl.grid(row=row_index, column=col, sticky="nsew")
                self.labels[(row_index, col)] = lbl

            # truck number label
            truck_lbl = tk.Label(
                self,
                text=associated_truck[truck_lbl_index],
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=3
            )
            truck_lbl.grid(row=row_index, column=9, sticky="nsew")

            truck_lbl_index += 1  # required to get each entry from associated_truck
            row_index += 1

        # Make columns expand equally
        for col in range(len(headers)):
            self.grid_columnconfigure(col, weight=1)

    # Updates package grid given a users input time
    def update_package_table(self, hr, start_row=0):
        hr = int(hr) # Users input time
        truck1_end = self.controller.get_truck(1)
        truck1_end = int(str(truck1_end.end_time)[:2]) + 1
        truck3_cargo = self.controller.get_all_cargo(3)[2]
        truck2_cargo = self.controller.get_all_cargo(2)[1]
        # Retrieves package data and displays it in a rows labels
        for package in self.package_data.table:
            if package is None:
                continue
            row = int(package[0] + 3)
            delivery_time = self.controller.package_status(package[0])
            if "@" in delivery_time:
                delivery_time = int(delivery_time.split("@")[1].strip()[:2])
                if delivery_time < hr:
                    self.labels[(row, 8)].config(text=package[8])
                else:
                    self.labels[(row, 8)].config(text="En Route")
            if hr < 11 and int(package[0]) == 9: # Keep wrong address for package displayed until updated
                self.labels[(row, 1)].config(text="300 State St")
                self.labels[(row, 2)].config(text="Salt Lake City")
                self.labels[(row, 4)].config(text="84103")
                self.labels[(row, 7)].config(text="Wrong address listed")
            else:
                self.labels[(row, 1)].config(text=package[1])
                self.labels[(row, 2)].config(text=package[2])
                self.labels[(row, 4)].config(text=package[4])
                self.labels[(row, 7)].config(text=package[7])
            if package[0] in truck2_cargo and hr < 10:
                self.labels[(row, 8)].config(text="Awaiting Delayed Packages")
            if hr < truck1_end and package[0] in truck3_cargo:
                self.labels[(row, 8)].config(text="@DEPOT Awaiting Driver")
            if hr < 8:
                self.labels[(row, 8)].config(text="At Depot")

    # Validates users input time from spinbox between 0-23
    def validate_hour(self, hr):
        try:
            hour = int(hr)
            if 0 <= hour <= 23:
                self.update_package_table(hour, start_row=3)
            else:
                print("Input Error:\nEntered time must be a number between 0-23")
                print(f'You entered:\nHour: {hr}')
        except ValueError:
            print("Input Error:\nEntered time must be a number between 0-23")
            print(f'You entered:\nHour: {hr}')

