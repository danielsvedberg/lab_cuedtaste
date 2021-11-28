#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 11:44:50 2020

@author: dsvedberg
"""
# TODO 01/13/21: make the sounds from the wav. files play alongside the visual cues
# search "TODO 01/13/21" to find areas where I think this will be implemented
# visit https://github.com/pygame/pygame/blob/main/examples/aliens.py for an example of how I think sounds could be implemented
# To try the aliens example, enter: python3 -m pygame.examples.aliens into terminal 
#
# Instructions for using blocks_sounds: 
# cd to the directory containing the folder containing blocks_sounds.py and audio files. 
# Enter: python3 blocks_sounds.py into terminal. 
# Use number keys 0-5 to switch the cue. 
# Click x or esc to exit.   

import pygame as pg
import os
#import receive_tone_values as receive
import multiprocessing as mp
import socket
import random #maybe import OS to start the recieve script?
 
# Define some colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)

# Set the height and width of the screen
screen_w = 800
screen_h = 480

def receive(signal):
    UDP_IP = "129.64.50.48"
    #when on phone
    #UDP_IP = "172.20.10.8"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, # internet
                        socket.SOCK_DGRAM) #UDP

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT)) 

    while True:
            data, addr = sock.recvfrom(1024) #buffer size is 1024 bytes
            if data:
                # send this to function that initiates tone/replace keyboard values
                signal.value = int.from_bytes(data, "big", signed="True")
                print("recieved message:", signal.value)

#added 5/26, mp the receive mehtod
def get_signal():
    return signal.value

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
            
            
def Blockset(number, speed):
    spritelist = pg.sprite.Group()
    width = screen_w/(number*2)
    for i in range(number+1):
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

#TODO 01/13/21: Currently unused. Should use this to load sounds and associate with each cue. Check pygame example "aliens" for demo. 
def load_sound(file):
    if not pg.mixer:
        return None
    pg.mixer.pause()
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None

if __name__ == "__main__":
    # Initialize Pygame
    pg.init()
    
    signal = mp.Value("i", 0)
    tone_values = mp.Process(target = receive, args = (signal,))
    tone_values.start()
    
    screen = pg.display.set_mode([screen_w, screen_h])
     
    # created a dictionary containing the .wav files
    audio_dict = {0: "pink_noise.wav", 1: "1000hz_sine.wav", 2: "3000hz_square.wav", 3: "5000hz_saw.wav", 4: "7000hz_unalias.wav"}
    # iterates through the dictionary to load the sound-values that correspond to the keys
    for key, value in audio_dict.items():
            audio_dict[key] = load_sound(value)
    # function called in the main loop to play new sound according to keypress, which is the "num" parameter
    def pause_play(num):
        pg.mixer.stop()
        audio_dict[num].play()


    cue_0 = Blockset(20,1)
    #TODO 01/13/21: example of using load sound from pygame, implement for every cue
    cue_1 = Blockset(20,-4)
    cue_2 = Blockset(30,-3)
    cue_3 = Blockset(40,-2)
    cue_4 = Blockset(50,-1)
    cue_5 = Blockset(1,0) 

    # Loop until the user clicks the close button.
    done = False
     
    # Used to manage how fast the screen updates
    clock = pg.time.Clock()
    cue = cue_5
    old_value = signal.value
    # -------- Main Program Loop -----------
    while not done:
        # Clear the screen
        screen.fill(WHITE)

        #This for-loop checks for key presses that changes the cue, and also to quite the program. 
        #TODO 01/13/21: in addition to switching the visual cues assigned to "cue", each event should also trigger the corresponding sound
        if old_value != get_signal():
            if get_signal() == 0:
                cue = cue_0
                pause_play(0)
                    #TODO 01/13/21: example of playing sound. Implement different sound for every cue, and turn off old sound when new cue triggered
            elif get_signal() == 1:
                cue = cue_1
                pause_play(1)
            elif get_signal() == 2:
                cue = cue_2
                pause_play(2)
            elif get_signal() == 3:
                cue = cue_3
                pause_play(3)
            elif get_signal() == 4:
                cue = cue_4
                pause_play(4)
            elif get_signal() == 5: # added June 1
                pg.mixer.stop()
                cue = cue_5 # added June 1
        # Go ahead and update the screen with what we've drawn.
        cue.update()
        cue.draw(screen)
        pg.display.flip()
        print("old value", old_value, "get signal", get_signal())
        old_value = signal.value
     
        # Limit to 60 frames per second
        clock.tick(60)
     
    pg.quit()
    tone_values.join()
