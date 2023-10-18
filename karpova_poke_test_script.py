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

if __name__ == "__main__":
    GPIO.cleanup() #turn off any pins that shouldn't be on
    GPIO.setmode(GPIO.BOARD) #initialize GPIO in "board mode", meaning pin numbers are mapped to the literal raspberry pi pin number, not GPIO number 
    
    poke = NosePoke(22,23) #initialize a nosepoke object. The LED is mapped to pin 22, and IR sensor is mapped to pin 23
    
    #just to demonstrate, turn the LED off for 1 second, and then back on again
    poke.led_off()    
    time.sleep(1) #pause for a second, otherwise the off/on will be instantanous 
    poke.led_on()
    
    #beam break demonstration: print in the terminal if poke is crossed or not, for [duration] seconds
    start = time.time()
    duration = 30
    end = start + duration 
    while time.time() < end:
        print(poke.is_crossed())
        time.sleep(0.1) #pause for 0.1s each loop, otherwise your terminal will be flooded with 
        
    GPIO.cleanup()