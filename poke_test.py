#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:26:51 2023

@author: dsvedberg
"""
import RPi.GPIO as GPIO
import time

#for ease of use, this example sets up the nosepoke as an object with callable functions
class NosePoke:
    def __init__(self, led_pin, ir_pin):
        self.led = led_pin #define the NosePoke's LED pin mapping
        self.ir = ir_pin #define the NosePoke's IR pin mapping
        #initialize the GPIO pins mapped to the LED and IR:
        GPIO.setup(self.led, GPIO.OUT) 
        GPIO.setup(self.ir, GPIO.IN)
    
    #note that the LED control is backwards of what you'd expect. Turning the pin on dims the LED
    def led_off(self):  # turn the light off
        GPIO.output(self.led, 1)
    
    def led_on(self):  # turn the light on
        GPIO.output(self.led, 0) 
        
    def is_crossed(self): #momentarily check if the ir beam is crossed
        return GPIO.input(self.ir) == 1 #if the IR beam is crossed, this function returns a True, otherwise False. 
    
    def light_test(self, duration = 20):
        start = time.time()
        end = start + duration 
        while time.time() < end:
            time.sleep(0.5)
            self.led_off()
            print("LED off")
            time.sleep(0.5)
            self.led_on()
            print("LED on")
        print("LED test complete")
        self.led_on()
        
    def poke_test(self, duration = 30):
        start = time.time()
        duration = 30
        end = start + duration 
        while time.time() < end:
            print(self.is_crossed())
            time.sleep(0.1) #pause for 0.1s each loop, otherwise your terminal will be flooded with 
            
def main_menu():
    options = ["LED test", "IR test",
               "exit"]
    print(67 * "-")
    print("MAIN MENU")
    for idx, item in enumerate(options):
        print(str(idx + 1) + ". " + item)
    print(67 * "-")
    choice = int(input("Enter your choice [1-" + str(len(options)) + "]: "))
    print("option "+str(choice) + " selected")
    return choice

if __name__ == "__main__":
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) #initialize GPIO in "board mode", meaning pin numbers are mapped to the literal raspberry pi pin number, not GPIO number 
    poke = NosePoke(15,13) #initialize a nosepoke object. The LED is mapped to pin 22, and IR sensor is mapped to pin 23

    while True:
        choice = main_menu()
        try:
            if choice == 1:
                poke.light_test(duration = 20)
            elif choice == 2: 
                poke.poke_test()
            elif choice == 3:
                print("program exit")
                GPIO.cleanup()
                break
        except ValueError:
            print("please enter a valid number: ")