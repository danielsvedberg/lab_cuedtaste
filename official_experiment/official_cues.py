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
# Define some colors
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)

# Set the height and width of the screen
screen_w = 800
screen_h = 480

image_dict = {1: 'vertical.jpeg', 2: 'vertical.jpeg', 3: 'left_slant.jpeg', 4: 'right_slant.jpeg'}

class Block(pg.sprite.Sprite):
    """
    This class represents the ball.
    It derives from the "Sprite" class in pg.
    """

    def __init__(self, color, width, speed_x, speed_y):
        """ Constructor. Pass in the color of the block,
        and its size. """

        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.width = width
        self.height = screen_h
        # self.image = pg.Surface([width, self.height])
        if color != BLACK:
            self.image = pg.transform.scale(color, (self.width, screen_h))
            screen.blit(color, (width, self.height))
        else: 
            self.image = pg.Surface([width, self.height])
            self.image.fill(color)
        self.speed_x = speed_x
        self.speed_y = speed_y

        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.origin_x = self.rect.x
        self.origin_y = self.rect.y

    # if self.speed is positive, blocks move right, and if it's negative, blocks move left
    def update(self):
        self.rect = self.rect.move(self.speed_x, self.speed_y)
        if self.speed_x < 0 and self.rect.left <= self.origin_x - self.width*2:
            self.rect.left = self.origin_x
        elif self.speed_x > 0 and self.rect.right >= self.origin_x + self.width*2:
            self.rect.right = self.origin_x

# blocket is now modified to make a large block pass through the screen very fast to appear as flashing, rather than many bars moving
def Blockset(number, speed_x, speed_y, cue=None):  # instead of number of blocks, number now determines how long block is, which you modulate to change frequency
    spritelist = pg.sprite.Group()
    width = screen_w*(number*10)
    # width = screen_w
    for i in range(12):
        if cue != None:
            # This represents a block
            block = Block(cue, width, speed_x, speed_y)
        else:
            block = Block(BLACK, width, speed_x, speed_y)
        # Set location for the block
        block.rect.x = width*2*i
        block.rect.y = 0
        block.origin_x = block.rect.x
        block.origin_y = block.rect.y
        # Add the block to the list of objects
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

# iterates through the dictionary to load the image-values that correspond to the keys
for key, value in image_dict.items():
    image_dict[key] = pg.image.load(value)

ser = serial.Serial('/dev/ttyS0', baudrate = 19200, timeout = 0.002)
ser.flushInput()
ser.flushOutput()
sig_ID = 0  # transfers the unique ID from receive function to main program
#cueend = 10
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

# created a dictionary containing the .wav files
audio_dict = {0: "9000hz_sine.wav",
              1: "20000_square.wav", 
              2: "7000hz_unalias.wav", 
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
    if num == 4:
        audio_dict[num].play(-1)
    else:
        pg.mixer.stop()
        audio_dict[num].play()

# This is a list of 'sprites.' Each block in the program is
# added to this list. The list is managed by a class called 'Group.'
cue_0 = Blockset(1,-80,0, image_dict[1]) #smaller value for "number" = faster flashing
cue_1 = Blockset(1,80,0, image_dict[2])  #bare minimum speed needed for flashing is 1000
# cue_1 = Blockset(1,100,0, image_dict[2])  #bare minimum speed needed for flashing is 1000
cue_2 = Blockset(1,-100,0, image_dict[3])
cue_3 = Blockset(1,100,0, image_dict[4])
cue_4 = Blockset(1,0,0)
cue_5 = Blockset(0,0,0)

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
        #screen.fill(BLACK)
        #pg.display.flip()
        
    if signal != 4 and signal != 5 and signal != 6 and time.time() >= now + 1:
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
