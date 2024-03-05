# Main Program

import sys
import pygame
import os
import math
from os import path
import tkinter as tk
from trackStats import *
from getStats import *
from gameRosterScreen import *


if __name__ == "__main__":
    root = tk.Tk()
    # Original screen dimensions
    scaled_w = 1920
    scaled_h = 1080

    # Directories
    img_dir = path.join(path.dirname(__file__), 'img')

    # Increas Dots Per inch so it looks sharper
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

    os.environ['SDL_VIDEO_CENTERED'] = '1' # You have to call this before pygame.init()

    # Pygame Configuration
    pygame.init()
    #fps = 1000
    fpsClock = pygame.time.Clock()
    info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
    # Scaling Ratios
    width_ratio = info.current_w/scaled_w
    height_ratio = info.current_h/scaled_h
    screen_width,screen_height = info.current_w - 10*width_ratio, info.current_h - 60*height_ratio
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    # Variables

    # font size
    font_size20 = int(20 * height_ratio)
    font_size32 = int(32 * height_ratio)

    # Our Buttons will append themself to this list
    objects = []

    # Other colors
    red_color = [255, 0, 0]
    green_color = [0, 255, 0]
    black_color = [0, 0, 0]
    grey_color = '#808080'


    # Button Variables
    buttonWidth = 250*width_ratio
    buttonHeight = 150*height_ratio
    buttonBumper = 30*width_ratio

    # Input Boxes Variables
    box_width = 140*width_ratio
    box_height = 32*height_ratio
    box_bumper = buttonBumper/3

    # Buttons and their respective functions.
    temp_button = None

    buttons = [
        ['Track Game Stats', lambda: gameRoster()],
        ['Get Stats', lambda: getStats()]
    ]

    # Making the buttons
    for index, buttonDetails in enumerate(buttons):
        temp_button = NormalButton((screen_width/2  - (len(buttons)/2*(buttonWidth + buttonBumper))) + (index * (buttonWidth + buttonBumper)), buttonBumper*3, buttonWidth, buttonHeight, font_size32, buttonDetails[0], buttonDetails[1])
        objects.append(temp_button)
    
    
    quit = False

    # Game loop.
    while not quit:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                pygame.quit()
                sys.exit()

            # for box in input_boxes_list:
            #     box.handle_event(event, input_boxes_list)

        # Drawing the Buttons
        for object in objects:
            object.process()
            screen.blit(object.buttonSurface, object.buttonRect)
        
        # Drawing the Input Boxes
        # for box in input_boxes_list:
        #     box.rect.w = max(200*width_ratio, (box.txt_surface.get_width()+10))
        # for box in input_boxes_list:
        #     box.draw(screen)


        pygame.display.flip()
        #fpsClock.tick(fps)
        fpsClock.tick()
