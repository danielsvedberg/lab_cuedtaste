# main_menu() shows the user the main menu and receives input
def main_menu():
    options = ["clearout a line", "set tastes", "calibrate a line", "cuedtaste",
               "exit"]
    print(67 * "-")
    print("MAIN MENU")
    for idx, item in enumerate(options):
        print(str(idx + 1) + ". " + item)
    print(67 * "-")
    choice = int(input("Enter your choice [1-" + str(len(options)) + "]: "))
    print("option "+str(choice) + " selected")
    return choice

# clearout_menu() runs a submenu of main_menu() for navigating clearouts of taste tubes.
def clearout_menu():
    while True:
        for x in range(1, 5):
            print(str(x) + ". clearout line " + str(x))
        print("5. main menu")
        line = int(input("enter your choice: "))
        if line in range(1, 6):
            print("line "+str(line)+" selected")
            return (line - 1)
        else:
            print("enter a valid menu option")

# calibration_menu() runs a submenu of main_menu() for navigating calibration of taste valves.
def calibration_menu():
    while True:
        for x in range(1, 5):
            print(str(x) + ". calibrate line " + str(x))
        print("5. main menu")
        line = int(input("enter your choice: "))
        if line in range(1, 6):
            return line - 1
        else:
            print("enter a valid menu option")

# taste_set_menu() runs a submenu of main_menu() for navigating calibration of taste valves.
def taste_set_menu():
    while True:
        print("1. set tastes")
        print("2. main menu")
        choice = int(input("enter your choice: "))
        if choice in range(1, 3):
            return choice
        else:
            print("enter a valid menu option")

# system_report() prints a system report of calibrations and tastes
def system_report():
    line_no = 1
    print(67 * "-")

    print("SYSTEM REPORT:")
    for i in lines:
        print("line: " + str(line_no) + "    opentime: " + str(i.opentime) + " s" + "   taste: " + str(i.taste))
        line_no = line_no + 1

## might need to be moved, but is here for now - gets params for current run
def get_cuedtaste_params():
    anID = str(input("enter animal ID: "))
    runtime = int(input("enter runtime in minutes: "))
    crosstime = int(input("enter crosstime in seconds: ")) #TODO: incorporate into .ini file, and make a function to update it
    # make variable called start with current moment in time
    start = datetime.datetime.now()
    dt = start.strftime("%Y%m%d_%Hh%Mm")
    rec_folder = anID + "_" + dt
    # create destination folder for data under Documents/cuedtaste_data/animalID if one doesn't exist
    dest_folder = "/home/blechpi/Documents/cuedtaste_data/" + anID + "/" + rec_folder
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print("created folder " + dest_folder)

    return anID, runtime, crosstime, dest_folder, start
