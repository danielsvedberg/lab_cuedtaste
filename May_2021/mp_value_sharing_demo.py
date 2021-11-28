#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 27 13:22:51 2021

@author: dsvedberg
"""
import multiprocessing as mp

def receive(signal):
    old_signal = signal.value
    while True:
        if signal.value == 420:
            break
        if signal.value != old_signal:
            signal.value = signal.value + 1
            print("mp process signal changed to: ", signal.value)
            old_signal = signal.value

    
    
if __name__ == "__main__":
    
    signal = mp.Value("i", 0)
    test = mp.Process(target = receive, args = (signal,))
    test.start()
    
    while True:
        print("base process signal 1: ", signal.value )
        signal.value = int(input("enter signal"))
        print("base process signal 2: ", signal.value)
        if signal.value == 420:
            break
        
        
# test that demos how you can pass and edit an mp.value object between multiprocesses 
# enter 420 to terminate
# function receive() is run as a multiprocess, and it edits the value of signal whenever you enter a new one
