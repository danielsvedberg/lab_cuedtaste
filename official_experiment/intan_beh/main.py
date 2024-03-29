import os 
import RPi.GPIO as GPIO
import configparser
import json
from menus import *
from NosePoke import *

### SECTION 4: Menu control/"GUI", everything below runs on startup ###

if __name__=="__main__":
    # set up raspi GPIO board.
    GPIO.setwarnings(False)
    GPIO.cleanup() #turn off any GPIO pins that might be on
    GPIO.setmode(GPIO.BOARD)

    ser = serial.Serial('/dev/ttyS0', baudrate = 57600, timeout = 0.01)
    ser.flushInput()
    ser.flushOutput()
    
    sigs = [0,1,2,3] #TODO: what is going on here? Why is it 0-3 and then 5,6?
    # lines = [TasteCueLine(tasteouts[i], intanouts[i], opentimes[i], tastes[i], sigs[i], ser) for i in range(4)]
    base = Cue(5, ser)
    end = Cue(6, ser)
    
    # initialize nosepokes:
    rew = NosePoke(40, 38)  # initialize "reward" nosepoke. "Rew" uses GPIO pins 38 as output for the light, and 11 as
    # input for the IR sensor. For the light, 1 = On, 0 = off. For the sensor, 1 = uncrossed, 0 = crossed.
    trig = Trigger(13, 15, 4, ser)  # initialize "trigger" trigger-class nosepoke. GPIO pin 38 = light output,
    # 13 = IR sensor input. Trigger is a special NosePoke class with added methods to control a cue.
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
        tasteouts = [31, 33, 35, 37]  # GPIO pin outputs to taste valves. Opens the valve while "1" is emitted from GPIO,
        # closes automatically with no voltage/ "0"
        intanouts = [24, 26, 19, 21]  # GPIO pin outputs to intan board (for marking taste deliveries in neural data). Sends
        # signal to separate device while "1" is emitted.
        # initialize taste-cue objects:
        intanDINs = [0,1,2,3]

        lines = [TasteCueLine(tasteouts[i], intanouts[i], opentimes[i], tastes[i], sigs[i], ser) for i in range(4)]
        
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
