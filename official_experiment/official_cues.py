#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 11:44:50 2020
bugs fixed
@author: dsvedberg || emmabarash
"""

#TODO: Dig in to intan
# visit https://github.com/pygame/pygame/blob/main/examples/aliens.py for an example of how I think sounds could be implemented
# To try the aliens example, enter: python3 -m pygame.examples.aliens into terminal
#
# Instructions for using blocks_sounds:
# cd to the directory containing the folder containing blocks_sounds.py and audio files.
# Enter: python3 blocks_sounds.py into terminal.
# Use number keys 0-5 to switch the cue.
# Click x or esc to exit.

from typing import overload
from xml.sax.handler import EntityResolver
import pygame as pg
import os
import time
import multiprocessing as mp
import socket
import random
import RPi.GPIO as GPIO
import serial
from math import ceil
import math

# Define some colors
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)

# Set the height and width of the screen
screen_w = 800
screen_h = 480

class Block(pg.sprite.Sprite):
    """
    This class represents the moving vertical bars.
    """

    def __init__(self, color, width, speed_x):
        """ Constructor. Pass in the color of the block, its width, and horizontal speed. """
        super().__init__()
        self.image = pg.Surface([width, screen_h])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed_x = speed_x

        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.origin_x = self.rect.x
        self.origin_y = self.rect.y

    # if self.speed is positive, blocks move right, and if it's negative, blocks move left
    def update(self):
        self.rect.x += self.speed_x
        if self.speed_x > 0 and self.rect.left > screen_w:  # For left-to-right movement
            self.rect.right = 0
        elif self.speed_x < 0 and self.rect.right < 0:  # For right-to-left movement
            self.rect.left = screen_w

''' this class creates the horizontal bars that travel up and down the screen'''
class HorizontalBar(pg.sprite.Sprite):
    def __init__(self, height, speed_y):
        super().__init__()
        self.image = pg.Surface([screen_w, height])
        self.image.fill(BLACK)  # Fill the bar with black color
        self.rect = self.image.get_rect()
        self.speed_y = speed_y  # Vertical speed

    def update(self):
        self.rect.y += self.speed_y
        # Wrap the bar around the screen
        if self.speed_y > 0 and self.rect.top > screen_h:  # Moving downwards
            self.rect.bottom = 0
        elif self.speed_y < 0 and self.rect.bottom < 0:  # Moving upwards
            self.rect.top = screen_h

def create_horizontal_bars(speed_y):
    bar_group = pg.sprite.Group()
    bar_height = 20  # Height of each bar
    spacing = bar_height  # Space between bars

    # Calculate the number of bars needed, accounting for spacing
    num_bars = (screen_h // (bar_height + spacing)) + 1

    for i in range(num_bars):
        bar = HorizontalBar(bar_height, speed_y)
        bar.rect.x = 0
        bar.rect.y = i * (bar_height + spacing)  # Position each bar with spacing
        bar_group.add(bar)


    return bar_group

class DiagonalBar(pg.sprite.Sprite):
    def __init__(self, screen_width, screen_height, speed_x, speed_y):
        super().__init__()
        diagonal_length = int(math.sqrt(screen_width**2 + screen_height**2))
        self.image = pg.Surface([diagonal_length, 5], pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Transparent background
        pg.draw.line(self.image, (0, 0, 0), (0, 0), (diagonal_length, 5), 5)  # Draw diagonal line

        # Initial position of the bar
        self.rect = self.image.get_rect(center=(-diagonal_length // 2, random.randint(0, screen_height)))

        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Check if the bar has moved off the screen
        if self.rect.right < 0 or self.rect.left > screen_w or self.rect.bottom < 0 or self.rect.top > screen_h:
            # Reset position
            self.rect.x = -self.rect.w
            self.rect.y = random.randint(0, screen_h)


# Function to create diagonal bars
def create_diagonal_bars(num_bars, speed_x, speed_y):
    bar_group = pg.sprite.Group()

    for _ in range(num_bars):
        bar = DiagonalBar(screen_w, screen_h, speed_x, speed_y)
        bar_group.add(bar)

    return bar_group

# blocket is now modified to make a large block pass through the screen very fast to appear as flashing, rather than many bars moving
def Blockset(speed_x, cue_num): 
    spritelist = pg.sprite.Group() 
    if cue_num == 4:
        pass
    elif cue_num == 5:
        block = Block(BLACK, screen_w, speed_x)
        spritelist.add(block)
    else:
        bar_width = 30  # Constant width for each bar

        num_bars = ceil(screen_w / (bar_width * 3)) + 1  # Number of bars needed

        for i in range(num_bars):
            block = Block(BLACK, bar_width, speed_x)
            block.rect.x = i * bar_width * 3  # Assuming a spacing of 3 times the width
            block.rect.y = 0
            spritelist.add(block)
    return spritelist

def load_sound(file):
    if not pg.mixer:
        return None
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None

# if __name__ == "__main__":
# Initialize Pygame
pg.init()

ser = serial.Serial('/dev/ttyS0', baudrate = 57600, timeout = 0.01)
ser.flushInput()
ser.flushOutput()
sig_ID = 0  # transfers the unique ID from receive function to main program
#cueend = 10
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

# created a dictionary containing the .wav files
audio_dict = {0: "15000_saw.wav",
              1: "9000hz_sine.wav", 
              2: "20000_square.wav", 
              3: "15000_saw.wav",
              4: "pink_noise.wav"}
# iterates through the dictionary to load the sound-values that correspond to the keys
for key, value in audio_dict.items():
    audio_dict[key] = load_sound(value)

pins = [11,13,15,16]
GPIO.setwarnings(False)
GPIO.cleanup() #turn off any GPIO pins that might be on
GPIO.setmode(GPIO.BOARD)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
# function called in the main loop to play new sound according to keypress, which is the "num" parameter
# if the signal is 5, the pink noise will play until the animal begins the next trial
# pink noise indicates the ability to start the next trial
# @run_once
def pause_play(num):
    pg.mixer.stop()
    if num == 4:
        audio_dict[num].play(-1)
    else:
        # pg.mixer.stop()
        audio_dict[num].play(-1)

# This is a list of 'sprites.' Each block in the program is
# added to this list. The list is managed by a class called 'Group.'
#TODO 01/13/21: example of using load sound from pygame, implement for every cue
cue_0 = Blockset(4, 0)
cue_1 = Blockset(-4, 1)
cue_2 = create_horizontal_bars(3)
cue_3 = create_horizontal_bars(-3)
cue_4 = Blockset(0, 4)
cue_5 = Blockset(0, 5)

cues = [cue_0,cue_1,cue_2,cue_3,cue_4,cue_5]

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pg.time.Clock()
# pause_play(0)  # to play white noise in the beginning

screen.fill(WHITE)
cue = cue_5
cue.update()
cue.draw(screen)
pg.display.flip()
clock.tick(60)
signal = 5 #this sets the base signal. Changed from 0 because signal for 0 was changed to a sine wave and blocks, which is not what we want
old_value = signal
old_ID = sig_ID  # dec. 2021


in_flag = 1  # in flag is used to condition the if statements below so that pause_play() is triggered only once when states change
cnums = [0,1,2,3]
played_nums = []
clock = pg.time.Clock() # Moved out of while loop
now = time.time()
cue = cues[signal]
# -------- Main Program Loop -----------
while not done:
    # Used to manage how fast the screen updates
    old_value = signal
    old_ID = sig_ID  # dec. 2021

    while ser.in_waiting > 0:
        #######################################################################
        received = ser.read(1).decode('utf-8', 'ignore')
        if received in ["0","1", "2", "3", "4", "5", "6"]:
            print(received, type(received))
            signal = int(received)
            ser.write(received.encode('utf-8'))
            #time.sleep(0.001)
            sig_ID = sig_ID + 1
            now = time.time()
    
    #while not done:
        # #if there's any situation where the signal changes without triggering signal == 5, this statement changes in_flag
    if sig_ID != old_ID or signal != old_value:
        print("old value", old_value, "get signal",
                signal, "old ID", old_ID, "new ID", sig_ID)
        in_flag = 0

    #if in_flag == 0:  # PRINT TO CONSOLE TEST 
       

    # Clear the screen
    screen.fill(WHITE)

    # This for-loop checks for key presses that changes the cue, and also to quit the program.
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            done = True
            
    if signal == 4 and in_flag == 0: #trigger open cue
        in_flag = 1
        pause_play(signal)
        cue = cues[signal]
        # screen.fill(WHITE)
        # pg.display.flip()
            
    if signal in cnums and in_flag == 0: #taste-offer cue
        cue = cues[signal]
        in_flag = 1
        pause_play(signal)
        #GPIO.output(pins[signal],1)
        last_pin = pins[signal]
        cueend = time.time() + 1
        #GPIO.output(pins[signal],0) #commented out to help with debugging

    if signal == 5 and in_flag == 0:  # stop cues/"blank" cu
        cue = cues[5] #this should replace the previously presented cue with a black screen
        in_flag = 1
        pg.mixer.stop()
        # screen.fill(BLACK)
        # pg.display.flip()
        
    if signal != 4 and signal != 5 and signal != 6 and time.time() >= now + 4: # play the cue for five seconds (for the first part of taste training)
            in_flag = 0
            signal = 5
            print('true')
            
    if signal == 6:
        in_flag = 0
        pg.mixer.stop()
        screen.fill(BLACK)
        done = True #this is what ends the program
        
    # Go ahead and update the screen with what we've drawn.
    #for entity in cue:
    # if cue not in [cue_4, cue_5]:
    cue.update()
    cue.draw(screen)
    pg.display.update()
    pg.display.flip()
        
    old_value = signal

    old_ID = sig_ID  # exchanges old ID value 

    
    clock.tick(80) # clock.tick() updates the clock, argument Limits to 60 frames per second

            #break #i think these are causing the program to exit early
    
ser.close()
pg.quit()
