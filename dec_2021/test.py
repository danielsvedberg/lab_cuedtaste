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
            counter.value = counter.value + 1
            print("\ncounter:",counter.value)
            print("mp process signal changed to: ", signal.value)
            old_signal = signal.value

    
    
if __name__ == "__main__":
    
    manager = mp.Manager()
    counter = manager.Value('i', 0)
    signal = mp.Value("i", 0)
    test = mp.Process(target = receive, args = (signal,))
    test.start()
    # manager.start()
    
    while True:
        print("base process signal 1: ", signal.value )
        print("extra counter:", counter.value)
        signal.value = int(input("enter signal"))
        print("base process signal 2: ", signal.value)
        if signal.value == 420:
            break
        
        
# test that demos how you can pass and edit an mp.value object between multiprocesses 
# enter 420 to terminate
# function receive() is run as a multiprocess, and it edits the value of signal whenever you enter a new one

#################################################################################### TEST 2
# import random
# import time

# start = time.time()

# counter = 0
# def test():
#     global counter
#     counter = counter + 1
#     return "hii"

# for i in range(4):
#     print(test())
#     print(counter)
    
# print(counter)

# if __name__ == '__main__':

#     isDone = False
#     while not isDone:
#         num = random.randint(0,5)
#         if num % 2 == 0:
#             counter = counter + 1
#             print(counter)
#         elif time.time() - start > 0.0005:
#             isDone = True
            
#     print("outside", counter)

#################################################################################### TEST 3
# from multiprocessing import Process
# import os

# def info(title):
#     print(title)
#     print('module name:', __name__)
#     print('parent process:', os.getppid())
#     print('process id:', os.getpid())

# def f(name):
#     info('function f')
#     print('hello', name)

# if __name__ == '__main__':
#     info('main line')
#     p = Process(target=f, args=('bob',))
#     p.start()
#     p.join()