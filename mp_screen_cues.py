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

# Define some colors
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)

# Set the height and width of the screen
screen_w = 800
screen_h = 480

class Block(pg.sprite.Sprite):
    """
    This class represents the ball.
    It derives from the "Sprite" class in pg.
    """

    def __init__(self, color, width, speed):
        """ Constructor. Pass in the color of the block,
        and its size. """

        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.width = width
        self.height = screen_h
        self.image = pg.Surface([width, self.height])
        self.speed = speed
        self.image.fill(color)

        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.origin_x = self.rect.x
        self.origin_y = self.rect.y

    # if self.speed is positive, blocks move right, and if it's negative, blocks move left
    def update(self):
        self.rect = self.rect.move(self.speed, 0)
        if self.speed < 0 and self.rect.left <= self.origin_x - self.width*2:
            self.rect.left = self.origin_x
        elif self.speed > 0 and self.rect.right >= self.origin_x + self.width*2:
            self.rect.right = self.origin_x

# blocket is now modified to make a large block pass through the screen very fast to appear as flashing, rather than many bars moving
def Blockset(number, speed):  # instead of number of blocks, number now determines how long block is, which you modulate to change frequency
    spritelist = pg.sprite.Group()
    width = screen_w*(number*10)
    for i in range(2):
        # This represents a block
        block = Block(BLACK, width, speed)
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

UDP_IP = "129.64.50.48"
# UDP_IP = "172.20.186.173"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,  # internet
                        socket.SOCK_DGRAM)  # UDP

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, UDP_PORT))

sig_ID = 0  # transfers the unique ID from receive function to main program

signal = 0

screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

# created a dictionary containing the .wav files
audio_dict = {0: "3000hz_square.wav",
              1: "5000hz_saw.wav", 
              2: "7000hz_unalias.wav", 
              3: "9000hz_sine.wav",
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
# if the signal is 0, the pink noise will play until the animal begins the next trial
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

cue_0 = Blockset(1.25,-1000) #smaller value for "number" = faster flashing
cue_1 = Blockset(1.35,-1000) #bare minimum speed needed for flashing is 1000
cue_2 = Blockset(1.75,-1000)
cue_3 = Blockset(2,-1000)
cue_4 = Blockset(1,1)
cue_5 = Blockset(0,0)

cues = [cue_0,cue_1,cue_2,cue_3,cue_4,cue_5]

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pg.time.Clock()
# pause_play(0)  # to play white noise in the beginning
old_value = signal
old_ID = sig_ID  # dec. 2021

screen.fill(WHITE)
cue = cue_5
cue.update()
cue.draw(screen)
pg.display.flip()
clock.tick(60)

in_flag = 0  # in flag is used to condition the if statements below so that pause_play() is triggered only once when states change
cnums = [0,1,2,3]
    
while not done:
    # Used to manage how fast the screen updates
    clock = pg.time.Clock()
    old_value = signal
    old_ID = sig_ID  # dec. 2021

    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    if data:
        # send this to function that initiates tone/replace keyboard values
        signal = int.from_bytes(data, "big", signed="True")
        # sets up a unique ID for each value received 
        sig_ID = sig_ID + 1
        print("received message:", signal, "ID", sig_ID)
        now = time.time()
    
        while not done:
            # #if there's any situation where the signal changes without triggering signal == 5, this statement changes in_flag
            if sig_ID != old_ID or signal != old_value:
                print(sig_ID, "old", old_ID)
                in_flag = 0

            if in_flag == 0:  # PRINT TO CONSOLE TEST 
                print("old value", old_value, "get signal",
                        signal, "old ID", old_ID, "new ID", sig_ID)

            # Clear the screen
            screen.fill(WHITE)

            # This for-loop checks for key presses that changes the cue, and also to quit the program.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    done = True
                    
            if signal == 4 and in_flag == 0: #trigger open cue
                pause_play(signal)
                cue = cues[signal]
                in_flag = 1
                    
            if signal in cnums and in_flag == 0: #taste-offer cue
                cue = cues[signal]
                pause_play(signal)
                GPIO.output(pins[signal],1)
                last_pin = pins[signal]
                cueend = time.time() + 1
                in_flag = 1

            if signal == 5 and in_flag == 0 and time.time() > cueend:  # stop cues/"blank" cue
                GPIO.output(last_pin,0)
                pg.mixer.stop()
                screen.fill(BLACK)
                in_flag = 0
                break 

            if signal == 6:
                pg.mixer.stop()
                in_flag = 0
                screen.fill(BLACK)
                done = True
            # Go ahead and update the screen with what we've drawn.
            #for entity in cue:
            cue.update()
            cue.draw(screen)
            pg.display.update()
            pg.display.flip()
            
            old_value = signal

            old_ID = sig_ID  # exchanges old ID value 

            # Limit to 60 frames per second
            clock.tick(60)

            if signal != 6 and signal != 7 and time.time() >= now + 2:
                signal = 5
                print('true')
                break

pg.quit()
