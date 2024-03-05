import sys
import pygame
import ctypes
import os
import math
import cv2
from os import path
from os import listdir
from PIL import Image as PImage
from PIL import ImageDraw
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import matplotlib.ticker as mtick
import numpy as np
from numpy import asarray
from trackDataObjects import *

player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
img_dir = path.join(path.dirname(__file__), 'img')

map_offset_x = 130
map_offset_y = 25

red_color = (204, 0, 0)
green_color = (0, 128, 43)
black_color = (0, 0, 0)
grey_color = '#808080'

def getFaceoffAreaPercents(zone_data):
    d_zone = [0, 0]
    n_zone = [0, 0]
    o_zone = [0, 0]
    left_side = [0, 0]
    right_side = [0, 0]
    for zone in range(len(zone_data)):
        if zone == 0 or zone == 1:
            d_zone[0] = d_zone[0] + zone_data[zone][0]
            d_zone[1] = d_zone[1] + zone_data[zone][1]
        if zone == 2 or zone == 3 or zone == 4 or zone == 5 or zone == 6:
            n_zone[0] = n_zone[0] + zone_data[zone][0]
            n_zone[1] = n_zone[1] + zone_data[zone][1]
        if zone == 7 or zone == 8:
            o_zone[0] = o_zone[0] + zone_data[zone][0]
            o_zone[1] = o_zone[1] + zone_data[zone][1]
        if zone == 0 or zone == 2 or zone == 3 or zone == 7:
            left_side[0] = left_side[0] + zone_data[zone][0]
            left_side[1] = left_side[1] + zone_data[zone][1]
        if zone == 1 or zone == 5 or zone == 6 or zone == 8:
            right_side[0] = right_side[0] + zone_data[zone][0]
            right_side[1] = right_side[1] + zone_data[zone][1]
    if d_zone[1] != 0:
        d_percent = round((d_zone[0]/d_zone[1])*100, 2)
    else:
        d_percent = 0
    if n_zone[1] != 0:
        n_percent = round((n_zone[0]/n_zone[1])*100, 2)
    else:
        n_percent = 0
    if o_zone[1] != 0:
        o_percent = round((o_zone[0]/o_zone[1])*100, 2)
    else:
        o_percent = 0
    if left_side[1] != 0:
        left_percent = round((left_side[0]/left_side[1])*100, 2)
    else:
        left_percent = 0
    if right_side[1] != 0:
        right_percent = round((right_side[0]/right_side[1])*100, 2)
    else:
        right_percent = 0
    return d_percent, n_percent, o_percent, left_percent, right_percent

def faceoffMap(zone_data):
    
    img_dir = path.join(path.dirname(__file__), 'img')
    #image = PImage.open(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png"))
    image = PImage.open(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png"))
    
    box_size = (20, 70)
    # zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
    #box_cords = [(200, 210), (200, 515), (425, 210), (735, 210), (580, 360), (425, 515), (735, 510), (980, 215), (980, 515)]
    box_cords = [(170, 210), (170, 515), (425, 210), (695, 210), (550, 360), (425, 515), (695, 510), (940, 215), (940, 515)]
    
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial", 28, encoding='unic')
    for zone in range(len(zone_data)):
        win_total = zone_data[zone][0]
        total = zone_data[zone][1]
        if total != 0:
            percent = round((win_total/total)*100, 2)
        else:
            percent = 0
        if percent > 50:
            color = green_color
        else:
            color = red_color
        line_text = str(percent) + "% (" + str(win_total) + "/" + str(total) +  ")"
        width, height = font.getsize(line_text)
        draw.text((box_cords[zone][0], box_cords[zone][1]), line_text, font=font, fill=color)

    # convert ot a pygame surface
    mode = image.mode
    size = image.size
    data = image.tobytes()

    image = pygame.image.fromstring(data, size, mode)

    # scale image
    image = pygame.transform.smoothscale(image, (image.get_size()[0]*(2/3), image.get_size()[1]*(2/3)))

    #image.show()
    return image

def locationmap1point(data):
    #image = PImage.open(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png"))
    image = PImage.open(path.join(img_dir, "hockey-rink-diagram.png"))
    #image = np.array(image)
    r = 5
    for obj in data:
        if obj.on_net:
            color = green_color
        else:
            color = red_color
        x = obj.x + map_offset_x
        y = obj.y + map_offset_y
        draw = ImageDraw.Draw(image)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)
    #image.show()

    # Save
    #cv2.imwrite("result.png", image)

    return image

def shotlocationmap1point(shot_data, goal_data, goalie):
    if goalie:
        map_offset_x = -20
        map_offset_y = 25
        x_color = (0, 0, 204)
        scalar = 6/5
        for obj in shot_data:
            obj.x = obj.x*scalar
        for obj in goal_data:
            obj.x = obj.x*scalar

    else:
        map_offset_x = 130
        map_offset_y = 25
        x_color = (255, 0, 0)

    image = cv2.imread(path.join(img_dir, "hockey-rink-diagram.png"))
    height, width, channels = image.shape


    r = 7
    # drawing dots for the shots
    for obj in shot_data:
        if obj.on_net:
            color = (43, 128, 0) #green
        else:
            color = (0, 0, 204) #red
        x = int(obj.x + map_offset_x)
        y = int(obj.y + map_offset_y)
        cv2.circle(image, (x, y), r, color, -1)
  

    line_length = 10
    # drawing X's for the goals
    for obj in goal_data:
        x = int(obj.x + map_offset_x)
        y = int(obj.y + map_offset_y)
        # Drawing the lines 
        cv2.line(image, (x-line_length, y-line_length), (x+line_length, y+line_length), x_color, 5) 
        cv2.line(image, (x-line_length, y+line_length), (x+line_length, y-line_length), x_color, 5)

    # Crop rink in half
    if goalie:
        image = image[80:height-50, 0:int(width/2)]
        height, width = image.shape[:2]
    else:
        image = image[80:height-50, int(width/2):width]
        height, width = image.shape[:2]
    #cv2.imshow('image', image)

    # Save
    #cv2.imwrite("result.png", image)

    # fix colors
    image = image[:,:,::-1]

    # make it a surface and flip it
    image = pygame.surfarray.make_surface(image)
    image = pygame.transform.flip(image, True, False)
    if goalie:
        image = pygame.transform.flip(image, True, False)
        image = pygame.transform.flip(image, True, False)
    # scale image
    #image = pygame.transform.smoothscale(image, (image.get_size()[0]*(4/5), image.get_size()[1]*(4/5)))

    return image

def locationmap2point(data):
    #image = PImage.open(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png"))
    image = PImage.open(path.join(img_dir, "hockey-rink-diagram.png"))
    na = np.array(image)
    #image = np.array(image)
    r = 5
    for obj in data:
        if obj.complete:
            color = green_color
        else:
            color = red_color
        start = (int(obj.start_x + map_offset_x), int(obj.start_y + map_offset_y))
        end = (int(obj.end_x + map_offset_x), int(obj.end_y + map_offset_y))
        na = cv2.arrowedLine(na, start, end, color, 8)
    
    image = PImage.fromarray(na)
    #image.show()

    # Save
    #cv2.imwrite("result.png", image)

    return image

def passlocationmap2point(pass_data, assist_data):
    #image = PImage.open(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png"))
    image = PImage.open(path.join(img_dir, "hockey-rink-diagram.png"))
    na = np.array(image)
    #image = np.array(image)
    
    for obj in pass_data:
        if obj.complete:
            color = green_color
        else:
            color = red_color
        start = (int(obj.start_x + map_offset_x), int(obj.start_y + map_offset_y))
        end = (int(obj.end_x + map_offset_x), int(obj.end_y + map_offset_y))
        na = cv2.arrowedLine(na, start, end, color, 8)

    for obj in assist_data:
        start = (int(obj.start_x + map_offset_x), int(obj.start_y + map_offset_y))
        end = (int(obj.end_x + map_offset_x), int(obj.end_y + map_offset_y))
        na = cv2.arrowedLine(na, start, end, (0, 0, 255), 8)
    
    #image = PImage.fromarray(na)
    image = na
    #image.show()

    # Save
    #cv2.imwrite("result.png", image)

    # fix colors
    #image = image[:,:,::-1]

    # make it a surface and flip it
    image = pygame.transform.flip(pygame.surfarray.make_surface(image), True, False)
    image = pygame.transform.rotate(image, 90)
    # scale image
    image = pygame.transform.smoothscale(image, (image.get_size()[0]*(2/3), image.get_size()[1]*(2/3)))

    return image

def single_fig_line(y, x, title, x_label, y_label, percent=False):
    # create a new figure
    fig= plt.figure(figsize=(10,6))
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=10)
    if percent:
        plt.yticks([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])
        plt.ylim(0, 1)
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.plot(x, y)

    #plt.show()

    # Convert matplotlib fig to a pygame surface
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    fig = pygame.image.fromstring(raw_data, size, "RGB")

    # scale image
    fig = pygame.transform.smoothscale(fig, (fig.get_size()[0]*(4/5), fig.get_size()[1]*(4/5)))

    # return it
    return fig

def multi_fig_line(y, x, title, x_label, y_label, legend_titles, percent=False):
    fig= plt.figure(figsize=(10,6))
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=10)

    if percent:
        plt.yticks([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])
        plt.ylim(0, 1)
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    
    for i in range(len(y)):
        plt.plot(x, y[i])
    plt.legend(legend_titles)
    
    #plt.show()

    # Convert matplotlib fig to a pygame surface
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    fig = pygame.image.fromstring(raw_data, size, "RGB")

    # scale image
    fig = pygame.transform.smoothscale(fig, (fig.get_size()[0]*(4/5), fig.get_size()[1]*(4/5)))

    # return it
    return fig

def shotsTimeGraph(shot_data_by_game, opponents):
    shots_by_game = []
    on_net_percentage_by_game = []
    for game in shot_data_by_game:
        shots_by_game.append(len(game))
        total_count = 0
        on_net_count = 0
        for shot in game:
            total_count = total_count + 1
            if shot.on_net:
                on_net_count = on_net_count + 1
        if total_count > 0:
            on_net_percentage_by_game.append(round(on_net_count/total_count, 2))
        else:
            on_net_percentage_by_game.append(0)

    # plt.plot(opponents, shots_by_game) 
    # plt.xlabel("Total Shots per Game")  # add X-axis label 
    # plt.ylabel("Games")  # add Y-axis label 
    # plt.title("Total Shots Taken")  # add title 
    # plt.show() 
    
    total_shots_fig = single_fig_line(shots_by_game, opponents, "Total Shots Taken", "Games", "Shots")

    on_net_percent_fig = single_fig_line(on_net_percentage_by_game, opponents, "Shooting On Net Percentage", "Games", "Percent On Net", True)

    # return it
    return total_shots_fig, on_net_percent_fig

def passTimeGraph(pass_data_by_game, opponents):
    pass_by_game = []
    complete_percentage_by_game = []
    complete_percentage_by_zone_by_game = [[], [], []]  #[D zone, N zone, O zone]
    for game in pass_data_by_game:
        pass_by_game.append(len(game))
        total_count = 0
        total_count_by_zone = [0, 0, 0]
        complete_count = 0
        complete_count_by_zone = [0, 0, 0]
        for Pass in game:
            total_count = total_count + 1
            total_count_by_zone[Pass.zone] = total_count_by_zone[Pass.zone] + 1
            if Pass.complete:
                complete_count = complete_count + 1
                complete_count_by_zone[Pass.zone] = complete_count_by_zone[Pass.zone] + 1
        if total_count > 0:
            complete_percentage_by_game.append(round(complete_count/total_count, 2))
        else:
            complete_percentage_by_game.append(0)
        for zone in range(3):
            if total_count_by_zone[zone] != 0:
                complete_percentage_by_zone_by_game[zone].append(round(complete_count_by_zone[zone]/total_count_by_zone[zone], 2))
            else:
                complete_percentage_by_zone_by_game[zone].append(0)

    # plt.plot(opponents, pass_by_game) 
    # plt.xlabel("Total pass per Game")  # add X-axis label 
    # plt.ylabel("Games")  # add Y-axis label 
    # plt.title("Total pass Taken")  # add title 
    # plt.show() 
    
    total_passes_fig = single_fig_line(pass_by_game, opponents, "Total Passes Taken", "Games", "Passes")
    total_percent_fig = single_fig_line(complete_percentage_by_game, opponents, "Passing Completion Percentage", "Games", "Percent Completed", True)
    zone_percent_fig = multi_fig_line(complete_percentage_by_zone_by_game, opponents, "Passing Completion Percentage by Zone", "Games", "Percent Completed", ["D-Zone", "Neutral Zone", "O-Zone"], True)


    # return it
    return total_passes_fig, total_percent_fig, zone_percent_fig

def faceoffTimeGraph(zone_data_by_game, opponents):
    # zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
    detailed_data_by_game = [[], [], [], [], []]
    total_win_percent_by_game = []
    for game in zone_data_by_game:
        d_zone, n_zone, o_zone, left_side, right_side = getFaceoffAreaPercents(game)
        detailed_data_by_game[0].append(d_zone/100)
        detailed_data_by_game[1].append(n_zone/100)
        detailed_data_by_game[2].append(o_zone/100)
        detailed_data_by_game[3].append(left_side/100)
        detailed_data_by_game[4].append(right_side/100)
        win_count = 0
        total_count = 0
        for zone in game:
            win_count = win_count + zone[0]
            total_count = total_count + zone[1]
        if total_count != 0:
            total_win_percent_by_game.append(round(win_count/total_count, 2))
        else: total_win_percent_by_game.append(0)

    detailed_percent_fig = multi_fig_line(detailed_data_by_game, opponents, "Faceoff Detailed Win Percentage", "Games", "Percent Won", ["D-Zone", "Neutral-Zone", "O-Zone", "Left Side", "Right Side"], True)
    total_percent_fig = single_fig_line(total_win_percent_by_game, opponents, "Faceoff Total Win Percentage", "Games", "Percent Won", True)

    return total_percent_fig, detailed_percent_fig


if __name__ == "__main__":

    data1 = []
    data2 = []

    data1.append(Shot((0, 0), True, 1, True, False, False, False))
    data1.append(Shot((50, 0), True, 1, True, False, False, False))
    data1.append(Shot((100, 0), True, 1, True, False, False, False))
    data1.append(Shot((0, 50), True, 1, True, False, False, False))
    data1.append(Shot((0, 100), True, 1, True, False, False, False))


    image = shotlocationmap1point(data1, data2)
    cv2.imshow('image', image)

