"""
Created on Mon Sep  9 14:15:36 2019

@author: Daniel Svedberg pre-2021 (dsvedberg@brandeis.edu)
@author: Emma Barash  2021-2022  (emmalala@brandeis.edu)
"""

#TODO: log cues in csv
from selectors import EpollSelector
import time
import multiprocessing as mp
import RPi.GPIO as GPIO
import os
import datetime
import random
import configparser
import json
import csv
import serial


########################################################################################################################
### SECTION 1: CLASSES ###

# NosePoke is a class that controls the physical nose poke device in the rig. Input variable light = GPIO pin for
# controlling LED in the nosepoke (1 = on, 0 = off). Input variable beam = GPIO pin receiving input from IR
# beam-break sensor inside nose poke device (1 = uncrossed, 0 = crossed)
class NosePoke:
    def __init__(self, light, beam, intanOut):
        self.exit = None
        self.light = light
        self.beam = beam
        self.intanOut = intanOut
        self.endtime = time.time() + 1200  # endtime is a class-wide condition to help the program exit when the task
        # is over. Usually this variable is changed when a behavioral task program is initiated
        GPIO.setup(self.light, GPIO.OUT)
        GPIO.setup(self.beam, GPIO.IN) 
        GPIO.setup(self.intanOut, GPIO.OUT)

    def shutdown(self):
        print("blink shutdown")
        self.exit.set()

    def flash_on(self):  # turn the light on
        GPIO.output(self.light, 0)

    def flash_off(self):  # turn the light off
        GPIO.output(self.light, 1)

    def flash(self, hz, run):  # bink on and of at frequency hz (LED has physical limit of 3.9)
        print("flashing "+str(self.light)+" start")
        while time.time() < self.endtime:
            if run.value == 1:
                GPIO.output(self.light, 1)
            if run.value == 1:
                time.sleep(2 / hz)            # try to consolidate 
                GPIO.output(self.light, 0)    # test
            if run.value == 1:
                time.sleep(2 / hz)
            if run.value == 0:
                GPIO.output(self.light, 0)
            if run.value == 2:
                GPIO.output(self.light, 1)
        print("flashing "+str(self.light)+" start")

    def is_crossed(self):  # report if beam is crossed
        if GPIO.input(self.beam) == 1:
            GPIO.output(self.intanOut, 1)
        else:
            GPIO.output(self.intanOut, 0)
        
        return (GPIO.input(self.beam) == 1)
          
    def keep_out(self, wait):  # report when the animal has stayed out of the nosepoke for duration of [wait] seconds
        print("keep out start")
        start = time.time()
        while True and time.time() < self.endtime:
            if self.is_crossed():
                start = time.time()
            elif time.time() - start > wait:
                break
        print("keep out end")

    def kill(self):  # kind of useless method
        GPIO.output(self.light, 0)


# cue is a class that controls playback of a specific file. I imagine this class will be changed so that play_cue
class Cue:
    
    def __init__(self, signal, ser): 
        self.signal = signal
        self.cuestate = False
        self.ser = ser
        self.MESSAGE = str(self.signal).encode('utf-8')

    def play_cue(self):
        self.cuestate = True #changing cuestate hopefully will get caught by the record system
        print('raw', self.MESSAGE)
        
        #time.sleep(0.001)
        #received = ser.read(1)
        #while not received == self.MESSAGE: #commented out handshake to keep it lightweight
        #end = time.time()+0.001
        #while time.time() < end: #bombard recipient for 1 second
        ser.write(self.MESSAGE)
        #time.sleep(0.001)
        #received = ser.read(1)
        print("message:", self.MESSAGE)
        self.cuestate = False
        
    def is_playing(self):
        return ser.read(1) == self.MESSAGE 

# Trigger allows a NosePoke and cue to be associated
class Trigger(NosePoke, Cue):
    def __init__(self, light, beam, signal, intanOut, ser):
        NosePoke.__init__(self, light, beam, intanOut)
        Cue.__init__(self, signal, ser)


# class TasteLine controls an individual taste-valve and its associated functions: clearouts,
# calibrations, and deliveries. Use TasteLine by declaring a TasteLine object, using clearout() to clear-out,
# and then running calibrate() to set the opentime value. This opentime will be saved and used whenever deliver() is
# run.
class TasteLine:
    def __init__(self, valve, intanOut, opentime, taste):
        self.valve = valve  # GPIO pin number corresponding to the valve controlling taste delivery
        self.intanOut = intanOut  # GPIO pin number used to send a signal to our intan neural recording system
        # whenever a taste is delivered.
        self.opentime = opentime  # how long the valve stays open for one single delivery
        self.taste = taste  # string containing name of the corresponding taste, used for datalogging in record()

        # generating a tasteLine object automatically sets up the GPIO pins:
        GPIO.setup(self.valve, GPIO.OUT)
        GPIO.setup(self.intanOut, GPIO.OUT)

    def clearout(self):  # when starting up the rig, we need to clear the air from the tubes leading to the taste
        # delivery system, and clean out the tubes when we are done. clearout() prompts user to input how long the
        # valve should be open to clear the tube, and then clears out the tube for that duration.
        dur = float(input("enter a clearout time to start clearout, or enter '0' to cancel: "))
        print("clearout = " + str(dur) + "s")
        if dur == 0:
            print("clearout canceled")
            return
        print("clearout started")
        GPIO.output(self.valve, 1)
        time.sleep(dur)
        GPIO.output(self.valve, 0)
        print("clearout complete")

    def calibrate(self):  # when starting the rig, we need to calibrate how long valves should stay open for each
        # delivery, to ensure amount of liquid delivered is consistent from session to session. calibrate() prompts
        # user to input a calibration time, and then opens the valve 5 times for that time, so the user can weigh out
        # how much liquid is dispensed per delivery.
        opentime = float(input("enter an opentime (like 0.05) to start calibration: "))
        isSet = False
        while isSet == False:
            # Open ports
            for rep in range(5):
                GPIO.output(self.valve, 1)
                time.sleep(opentime)
                GPIO.output(self.valve, 0)
                time.sleep(3)
            ans = input('keep this calibration? (y/n): ')
            if ans == 'y':
                self.opentime = opentime
                print("opentime saved")
                isSet = True
            else:
                opentime = int(input('enter new opentime: '))
                isSet = False
                

    def deliver(self):  # deliver() is used in the context of a task to open the valve for the saved opentime to
        # deliver liquid through the line
        print("taste "+str(self.valve)+" open")
        GPIO.output(self.valve, 1)
        GPIO.output(self.intanOut, 1)
        time.sleep(self.opentime)
        GPIO.output(self.valve, 0)
        GPIO.output(self.intanOut, 0)
        print("taste "+str(self.valve)+" closed")

    def kill(self):
        GPIO.output(self.valve, 0)
        GPIO.output(self.intanOut, 0)
                                                       
    def is_open(self):  # reports if valve is open
        return GPIO.input(self.valve)

def set_tastes():  # when starting the rig, we need to log the tastes we are using so that they correspond to the lines that are being used.
    print("1. main menu")
    tastes = input("Please set the taste for each line: ")
    return tastes
           

# TastecueLine allows for a cue to be associated with a corresponding TasteLine
class TasteCueLine(TasteLine, Cue):
    def __init__(self, valve, intanOut, opentime, taste, signal, ser):
        TasteLine.__init__(self, valve, intanOut, opentime, taste)
        Cue.__init__(self, signal, ser)


### SECTION 2: MISC. FUNCTIONS

# record() logs sensor and valve data to a .csv file. Typically instantiated as a multiprocessing.process
def record(poke1, poke2, lines, starttime, endtime, anID, dest_folder, start):
    print("recording started")
    start_date = start.strftime("%Y%m%d_%Hh%Mm")
    filename = anID + "_" + start_date + "_cuedtaste.csv"
    filepath = os.path.join(dest_folder, filename)
    with open(filepath, mode='w') as record_file:
        fieldnames = ['Time', 'Poke1', 'Poke2', 'Line1', 'Line2', 'Line3', 'Line4', 'Cue1', 'Cue2', 'Cue3', 'Cue4']
        record_writer = csv.writer(record_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        record_writer.writerow(fieldnames)
        while time.time() < endtime:
            data = [poke1.is_crossed(), poke2.is_crossed()]
            for item in lines:
                data.append(item.is_open())
            for item in lines:
                data.append(item.is_playing())
            if any(i == True for i in data):
                [str(i) for i in data]
                t = [str(round(time.time() - starttime, 3))]
                t.extend(data)
                record_writer.writerow(t)
            #time.sleep(0.001)
    print("recording ended")


# main_menu() shows the user the main menu and receives input
# TODO make a new option for setting the tastes
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

### SECTION 3: BEHAVIORAL TASK PROGRAMS ###
used_lines = []
def generate_sig(used_lines):
    print('used:', used_lines, "len", len(used_lines))
    # signal = random.randint(0,3) ### use for all four tastes
    signal = random.randint(0,2)
    
    # if len(used_lines) == 4: ### use for all four tastes
    if len(used_lines) == 3:
        used_lines.clear()

    if signal in used_lines:
        print('old sig', signal)
        # signal = int(random.choice([i for i in [0,1,2,3] if i not in used_lines])) ### use for all four tastes
        signal = int(random.choice([i for i in [0,1,2] if i not in used_lines]))
        print ('new sig', signal)
    
    used_lines.append(signal) #is this actualy appending?
    return signal
    
##cuedtaste is the central function that runs the behavioral task.
def cuedtaste(anID, runtime, crosstime, dest_folder, start):

    starttime = time.time()  # start of task
    endtime = starttime + runtime * 60  # end of task
    rew.endtime = endtime
    trig.endtime = endtime

    recording = mp.Process(target=record, args=(rew, trig, lines, starttime, endtime, anID, dest_folder, start,))

    recording.start()

    state = 0  # [state] controls state of task. Refer to PDF of hand-drawn diagram for visual guide

    # this loop controls the task as it happens, when [endtime] is reached, loop exits and task program closes out
    trig.flash_off()
    rew.flash_off()

    trial_dur = crosstime + 1
    trial_end = time.time()

    while time.time() <= endtime: 
        while state == 0 and time.time() <= endtime:  # state 0:
            if time.time() > trial_end:
                trig.flash_on()
                line = generate_sig(used_lines)
                trig.play_cue()
                state = 1
                print("new trial") #trigger light turns on to signal availability

        while state == 1 and time.time() <= endtime:  # state 1: new trial started/arming Trigger
            if trig.is_crossed():  # once the trigger-nosepoke is crossed, move to state 2
                print("cue number: ", str(line))
                trig.flash_off()
                lines[line].play_cue() # taste-associated cue cue is played
                print("trigger activated")
                rew.flash_on()
                deadline = time.time() + crosstime # rat has 10 sec to activate rewarder
                state = 2
                trial_end = time.time() + trial_dur # gates start of next trial to be no sooner than trial_dur
                time.sleep(1) #impose a 1 second delay to reward activation, hopefully allows cue to play out

        while state == 2 and time.time() <= endtime:  # state 3: Activating rewarder/delivering taste
            #time.sleep(0.01)
            if rew.is_crossed() and time.time():  # if rat crosses rewarder beam, deliver taste
                rew.flash_off()
                lines[line].deliver()
                print("reward delivered")
                state = 0
                base.play_cue() # make sure the cue stops playing after delivery

            if time.time() > deadline:  # if rat misses reward deadline, return to state 0
                rew.flash_off()
                state = 0
                base.play_cue()

    base.play_cue()  # kill any lingering cues after task is over
    end.play_cue()
    trig.flash_off()
    rew.flash_off()
    recording.join()  # wait for data logging and light blinking processes to commit seppuku when session is over
    print("assay completed")

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

#function that takes parameter inputs from cuedtaste() and logs them to a .txt file
def log_metadata(anID, runtime, crosstime, lines, dest_folder, start):
    #create .txt file with metadata
    #first, create a .txt in writemode, with a title composed of the animal ID, date, and time in hh:mm format, concatenated by underscores:
    d = start.strftime("%Y%m%d_%Hh%Mm")
    filename = anID + "_" + d + "_cuedtaste_metadata.txt"

    #create a filepath to the .txt file:
    filepath = os.path.join(dest_folder, filename)
    #create the .txt file in write mode:
    with open(filepath, mode='w') as metadata_file:
        #write the metadata to the .txt file:
        metadata_file.write("Animal ID: " + anID + "\n")
        metadata_file.write("Date: " + d + "\n")
        metadata_file.write("Runtime: " + str(runtime) + " minutes" + "\n")
        metadata_file.write("Crosstime: " + str(crosstime) + " seconds" + "\n")
        metadata_file.write("Origin Folder: " + dest_folder + "\n")
        #enter the tastes for each line into the .txt file as a list:
        metadata_file.write("Tastes: " + str([i.taste for i in lines]) + "\n")
        #enter the opentimes for each line into the .txt file as a list:
        metadata_file.write("Opentimes: " + str([i.opentime for i in lines]) + "\n")
        #enter the GPIO pins for each line into the .txt file as a list:
        metadata_file.write("ValvePins: " + str([i.valve for i in lines]) + "\n")
        #enter the intan GPIO pins for each line into the .txt file as a list:
        metadata_file.write("IntanPins: " + str([i.intanOut for i in lines]) + "\n")

########################################################################################################################

### SECTION 4: Menu control/"GUI", everything below runs on startup ###

if __name__=="__main__":
    # set up raspi GPIO board.
    GPIO.setwarnings(False)
    GPIO.cleanup() #turn off any GPIO pins that might be on
    GPIO.setmode(GPIO.BOARD)

    ser = serial.Serial('/dev/ttyS0', baudrate = 57600, timeout = 0.01)
    ser.flushInput()
    ser.flushOutput()
    
    sigs = [0,1,2] #TODO: what is going on here? Why is it 0-3 and then 5,6?
    # lines = [TasteCueLine(tasteouts[i], intanouts[i], opentimes[i], tastes[i], sigs[i], ser) for i in range(4)]
    base = Cue(5, ser)
    end = Cue(6, ser)
    
    # initialize nosepokes:
    rew = NosePoke(40, 38, 21)  # initialize "reward" nosepoke. "Rew" uses GPIO pins 38 as output for the light, and 11 as
    # input for the IR sensor. For the light, 1 = On, 0 = off. For the sensor, 1 = uncrossed, 0 = crossed.
    # 21 is the intan output that logs when the rewarder is crossed
    trig = Trigger(13, 15, 4, 7, ser)  # initialize "trigger" trigger-class nosepoke. GPIO pin 38 = light output,
    # 13 = IR sensor input. Trigger is a special NosePoke class with added methods to control a cue. 
    # 7 is the intan out to get information about when the poke is crossed.
    rew.flash_off()  # for some reason these lights come on by accident sometimes, so this turns off preemptively
    trig.flash_off()  # for some reason these lights come on by accident sometimes, so this turns off preemptively
    # flush input and output of serial

 # This loop executes the main menu and menu-options
    while True:

        # load configs
        config = configparser.ConfigParser()  # initialize configparser to read config file
        config.read("cuedtaste_config.ini")  # read config file
        opentimes = json.loads(config.get("tastelines", "opentimes"))  # load into array times to open valves when taste delivered
        tastes = json.loads(config.get("tastelines", "tastes"))  # load taste labels into list

        ## initialize objects used in task:
        # initialize tastelines w/cues
        tasteouts = [31, 33, 35]  # GPIO pin outputs to taste valves. Opens the valve while "1" is emitted from GPIO,
        # closes automatically with no voltage/ "0"
        intanouts = [24, 26, 19]  # GPIO pin outputs to intan board (for marking taste deliveries in neural data). Sends
        # signal to separate device while "1" is emitted.
        # initialize taste-cue objects:
        #trig_rew_outs = [7, 21]
        # used 0-2 are the solenoid valves 3 is trigger and 4 is rewarder
        intanDINs = [0,1,2,3,4]

        lines = [TasteCueLine(tasteouts[i], intanouts[i], opentimes[i], tastes[i], sigs[i], ser) for i in range(3)]
        
        ## While loop which will keep going until loop = False
        system_report()  # Displays valve opentimes and taste-line assignments
        choice = main_menu()  # Displays menu options
        try:
            if choice == 1:  # run clearout menu & clearout programs
                while True:
                    line = clearout_menu()
                    if line in range(4):
                        lines[line].clearout()
                    elif line == 4:
                        break
            elif choice == 2:  # run taste_set menu & taste_set programs
                while True:
                    taste = taste_set_menu()
                    if taste in range(2):
                        tastes = set_tastes()
                    elif taste == 2:
                        break
                    else:
                        print("input a valid line number")
                        break
                    
                    tastes = tastes.split(", ")
                    print("tastes", tastes)
                    # Format the items with double quotes and join them into a string
                    formatted_tastes = ', '.join(['"{}"'.format(item) for item in tastes])
                    formatted_tastes = "[" + formatted_tastes + "]"
                    print(formatted_tastes)
  
                    config.set('tastelines','tastes', str(formatted_tastes))
                    with open('cuedtaste_config.ini',
                            'w') as configfile:  # in python 3+, 'w' follows filename, while in python 2+ it's 'wb'
                        config.write(configfile)
                    

                    for line, taste in zip(lines, formatted_tastes):
                        line.taste = taste
            
            elif choice == 3:  # run calibration menu & calibration programs
                while True:
                    line = calibration_menu()
                    if line in range(4):
                        lines[line].calibrate()
                    elif line == 4:
                        break
                    else:
                        print("input a valid line number")
                        break

                    opentimes[line] = lines[line].opentime
                    config.set('tastelines', 'opentimes', str(opentimes))
                    with open('cuedtaste_config.ini',
                            'w') as configfile:  # in python 3+, 'w' follows filename, while in python 2+ it's 'wb'
                        config.write(configfile)

            elif choice == 4:  # run the actual program
                print("starting cuedTaste")
                anID, runtime, crosstime, dest_folder, start = get_cuedtaste_params()
                log_metadata(anID, runtime, crosstime, lines, dest_folder, start)
                cuedtaste(anID, runtime, crosstime, dest_folder, start)
            elif choice == 5:
                print("program exit")
                GPIO.cleanup()
                break

        except ValueError:
            print("please enter a number: ")
