# Imports
import sys
import pygame
import ctypes
import os
import math
from os import path
from pathlib import Path
from datetime import date
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

from extractData import *
from helpers import NormalButton
from helpers import GroupedButton
from helpers import ToggleButton
from helpers import InputBox

# directories
player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
#player_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
#game_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
# Handler Functions
def getDistance(pos1, pos2):
    return math.dist(pos1, pos2)

def scalePoint(cords):
    x = cords[0] * (1/width_ratio)
    y = cords[1] * (1/height_ratio)
    return (x, y)

def flipCordinates(cords):
    cords = (canvas.get_width() - cords[0], canvas.get_height() - cords[1])
    return cords

# get the 2 points farthest away from each other
def getEndPoints(pixels):
    # two points which are fruthest apart will occur as vertices of the convex hull
    candidates = pixels[spatial.ConvexHull(pixels).vertices]

    # get distances between each pair of candidate points
    dist_mat = spatial.distance_matrix(candidates, candidates)

    # get indices of candidates that are furthest apart
    i, j = np.unravel_index(dist_mat.argmax(), dist_mat.shape)
    return candidates[i], candidates[j]

# get list of pixels of a specific color
def getColoredPixels(pixels, color, canvas):
    colored_pixels = []
    for x in range(canvas.get_width()):
        for y in range(canvas.get_height()):
            if pixels[x, y] == canvas.map_rgb(color):
                colored_pixels.append((x, y))
    return colored_pixels

def determineIfHighDanger(cords):
    scaled_x_left = 810
    scaled_x_right = 1010
    scaled_y_top = 225
    scaled_y_bottom = 515
    if cords[0] > scaled_x_left and cords[0] < scaled_x_right and cords[1] > scaled_y_top and cords[1] < scaled_y_bottom:
        return True
    else:
        return False

# zones = [D-Zone, Neutral-Zone, O-Zone]
def determineZone(x):
    d_zone_blue_line = 370
    o_zone_blue_line = 730
    if x < d_zone_blue_line:
        return 0
    elif x > o_zone_blue_line:
        return 2
    elif x > d_zone_blue_line and x < o_zone_blue_line:
        return 1

# zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
def determineFaceoffZone(cords):
    d_zone_top = (210, 225)
    d_zone_bottom = (210, 515)
    n_zone_top_left = (395, 225)
    n_zone_top_right = (705, 225)
    n_zone_center = (550, 370)
    n_zone_bottom_left = (395, 515)
    n_zone_bottom_right = (705, 515)
    o_zone_top = (890, 225)
    o_zone_bottom = (890, 515)
    zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
    closest_dist = 1000000
    closest_zone = None
    for i in range(len(zones)):
        temp_dist = getDistance(cords, zones[i])
        if temp_dist < closest_dist:
            closest_dist = temp_dist
            closest_zone = i

    return closest_zone


# Clearing the Canvas
def clearCanvas():
    canvas.blit(rink_img, (0,0))
    if rink_flipped:
        rotated_surf = pygame.transform.rotate(canvas, 180)
        canvas.blit(rotated_surf, (0,0))

# Flip Canvas
def flipCanvas():
    global rink_flipped
    rotated_surf = pygame.transform.rotate(canvas, 180)
    canvas.blit(rotated_surf, (0,0))
    if rink_flipped:
        rink_flipped = False
    else:
        rink_flipped = True

# Save the surface
def saveEvent():
    # Find the player who did the action
    player_name = None
    goalie_name = None
    for i in range(len(player_action_buttons)-1):
        if player_action_buttons[i].alreadyPressed:
            player_name = player_action_buttons[i].name2

    # if no player then it was the opponent who did the action
    if player_name == None:
        team = "Opponent"
        # Find goalie in net
        for i in range(len(goalie_in_net_buttons)):
            if goalie_in_net_buttons[i].alreadyPressed:
                goalie_name = goalies_names[i]
        if goalie_name == None:
            Tk().wm_withdraw() #to hide the main window
            messagebox.showinfo('Player Error','No Goalie Selected')
            return
    else:
        team = "Buffs"

    # Find everyone who was on the ice
    on_ice = []
    for i in range(len(player_on_ice_buttons)):
        if player_on_ice_buttons[i].alreadyPressed:
            on_ice.append(full_player_roster[i])
    

    curr_date = date.today()
    pxarray = pygame.PixelArray(canvas)

    if event_type == "":
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Event Type Error','No Event Type Selected')
        return
    if period == 0:
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Period Error','No Period Selected')
        return
    

    # determine if the event was a success or failure
    if drawColor == red_color:
        complete = False
        pixels = getColoredPixels(pxarray, red_color, canvas)
    elif drawColor == green_color:
        complete = True
        pixels = getColoredPixels(pxarray, green_color, canvas)
    else:
        complete = None
        pixels = getColoredPixels(pxarray, black_color, canvas)

    if pixels == []:
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Drawing Error','Draw Something!')
        return

    # determine the location of the events
    if event_type == 'Pass' or event_type == '1st Assist' or event_type == '2nd Assist':
        # get end points of line
        start_pos, end_pos = getEndPoints(np.array(pixels))
        # get the center of all pixels
        x = [p[0] for p in pixels]
        y = [p[1] for p in pixels]
        centroid = (sum(x) / len(pixels), sum(y) / len(pixels))
        # find actual start and end positions
        if getDistance(start_pos, centroid) < getDistance(end_pos, centroid):
            temp_pos = start_pos
            start_pos = end_pos
            end_pos = temp_pos
        # flip coords if rink is flipped
        if rink_flipped == True:
            start_pos = flipCordinates(start_pos)
            end_pos = flipCordinates(end_pos)
        start_pos = scalePoint(start_pos)
        end_pos = scalePoint(end_pos)

    elif event_type == 'Shot' or event_type == 'Goal' or event_type == 'Faceoff':
        # get the center of all pixels
        x = [p[0] for p in pixels]
        y = [p[1] for p in pixels]
        centroid = (sum(x) / len(pixels), sum(y) / len(pixels))
        # flip coords if rink is flipped
        if rink_flipped == True:
            centroid = flipCordinates(centroid)
        centroid = scalePoint(centroid)

    # determine the Play Type
    even_strength = False
    power_play = False
    penalty_kill = False
    if play_type == "5 on 5":
        even_strength = True
    elif play_type == "PP":
        power_play = True
    elif play_type == "PK":
        penalty_kill = True



    # save data
    temp_obj = None
    if event_type == 'Pass':
        high_danger = determineIfHighDanger(end_pos)
        zone = determineZone(end_pos[0])
        temp_obj = Pass(start_pos, end_pos, complete, period, even_strength, power_play, penalty_kill, high_danger, zone)
        if player_name != None:
            game_object.our_team.addPass(temp_obj, player_name)
        else:
            game_object.opponent.addPass(temp_obj)
    elif event_type == 'Shot' or event_type == "Goal":
        high_danger = determineIfHighDanger(centroid)
        temp_obj = Shot(centroid, complete, period, even_strength, power_play, penalty_kill, high_danger)
        if player_name != None:
            game_object.our_team.addShot(temp_obj, player_name)
        else:
            game_object.opponent.addShot(temp_obj)
            game_object.our_team.addShot(temp_obj, goalie_name, True)
        # Goal
        if event_type == 'Goal':
            temp_obj = Goal(centroid, period, even_strength, power_play, penalty_kill, on_ice)
            if player_name != None:
                game_object.our_team.addGoal(temp_obj, player_name)
            else:
                game_object.opponent.addGoal(temp_obj)
                game_object.our_team.addGoal(temp_obj, goalie_name, True)
    elif event_type == 'Faceoff':
        zone = determineFaceoffZone(centroid)
        temp_obj = Faceoff(zone, complete, period)
        if player_name != None:
            game_object.our_team.addFaceoff(temp_obj, player_name)
        else:
            game_object.opponent.addfaceoff(temp_obj)
    elif event_type == '1st Assist':
        temp_obj = Assist(start_pos, end_pos, 1, period, even_strength, power_play, penalty_kill)
        if player_name != None:
            game_object.our_team.addAssist(temp_obj, player_name)
        else:
            game_object.opponent.addAssist(temp_obj)
    elif event_type == '2nd Assist':
        temp_obj = Assist(start_pos, end_pos, 2, period, even_strength, power_play, penalty_kill)
        if player_name != None:
            game_object.our_team.addAssist(temp_obj, player_name)
        else:
            game_object.opponent.addAssist(temp_obj)
    

    # Reset some parameters
    del pxarray
    clearCanvas()
    saveGame(game_object)
    return





# Handler Functions

# Make sure only 1 button is active/pressed at a time
def resetButtons(active_name, buttons):
    for button in buttons:
        if(button.name == active_name):
            button.alreadyPressed = True
        else:
            button.alreadyPressed = False

# Make sure only 1 button is active/pressed at a time
def resetButtons2(active_name, buttons):
    for button in buttons:
        if(button.name2 == active_name):
            button.alreadyPressed = True
        else:
            button.alreadyPressed = False

# Changing the Event Type
def changeEvent(new_event, buttons):
    global event_type
    event_type = new_event
    resetButtons(new_event, buttons)

# Changing the Brush Color
def changeColor(canvas, new_color, buttons):
    global drawColor
    pxarray = pygame.PixelArray(canvas)
    for x in range(canvas.get_width()):
        for y in range(canvas.get_height()):
            if pxarray[x, y] == canvas.map_rgb(drawColor):
                canvas.set_at((x,y), new_color)
    drawColor = new_color
    if new_color == red_color:
        resetButtons("Red", buttons)
    elif new_color == green_color:
        resetButtons("Green", buttons)
    elif new_color == black_color:
        resetButtons("Black", buttons)

# Changing the Period
def changePeriod(new_period, buttons):
    global period
    period = new_period
    if new_period == 1:
        name = "1st Period"
    elif new_period == 2:
        name = "2nd Period"
    elif new_period == 3:
        name = "3rd Period"
    elif new_period == 4:
        name = "OT"
    resetButtons(name, buttons)

# Play Type BUTTONS
def changePlayType(new_play_type, buttons):
    global play_type
    play_type = new_play_type
    resetButtons(new_play_type, buttons)

# Change Player Action Button
def changePlayerAction(name, buttons):
    resetButtons2(name, buttons)

def saveGame(game_object):
    # Save Game Object
    filename = game_path + str(date.today()) + "_" + game_object.opponent.team_name
    save_object(game_object, filename)
    # Reload Game Object
    game_object = load_object(filename)

def addShift(player_name):
    game_object.our_team.addShift(player_name)

def displayFaceoff():
    game_object.our_team.displayFaceoffData().show()
    return

def displayInGameStats():
    text = ''
    # Score
    Goals_for = len(game_object.our_team.goals)
    Goals_against = len(game_object.opponent.goals)
    text += "Score" + '\n'
    text += "For: " + str(Goals_for) + '\n'
    text += "Against: " + str(Goals_against) + '\n'

    # Shots
    shots_for = len(game_object.our_team.getOnNetShots())
    shots_against = len(game_object.opponent.getOnNetShots())
    text += '\n' + "Shots On Net:" + '\n'
    text += "For: " + str(shots_for) + '\n'
    text += "Against: " + str(shots_against) + '\n'

    # Faceoffs
    total_data, zone_data = game_object.our_team.getFaceoffData()
    total_data = total_data[:4] # get highest 4 players
    text += '\n' + "Faceoff %:" + '\n'
    for line in total_data:
        if line[1][1] == 0:
            percent = 0
        else:
            percent = round((line[1][0]/line[1][1])*100, 2)
        text += line[0] + ": " + str(percent) + "% (" + str(line[1][0]) + "/" + str(line[1][1]) +  ")" + '\n'
    
    Tk().wm_withdraw() #to hide the main window
    messagebox.showinfo('In Game Stats', text)
    return




def trackGameStats(full_player_roster_list, goalie_name_list, game_obj):
    global full_player_roster
    full_player_roster = full_player_roster_list
    global goalies_names
    goalies_names = goalie_name_list
    global game_object
    game_object = game_obj

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
    global width_ratio, height_ratio
    width_ratio = info.current_w/scaled_w
    height_ratio = info.current_h/scaled_h
    screen_width,screen_height = info.current_w - 10*width_ratio, info.current_h - 60*height_ratio
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    

    # Variables

    # font size
    font_size18 = int(18 * height_ratio)
    font_size20 = int(20 * height_ratio)
    font_size32 = int(32 * height_ratio)

    # Our Buttons will append themself to this list
    objects = []
    text_boxes = []

    # Initial brush size
    brushSize = 5*width_ratio

    # Drawing Area Size
    #canvasSize = [1260, 760]
    canvasSize = [1100*width_ratio, 720*height_ratio]

    # Button Variables
    buttonWidth = 150*width_ratio
    buttonHeight = 50*height_ratio
    buttonBumper = 10*width_ratio

    # Input Boxes Variables
    box_width = 140*width_ratio
    box_height = 32*height_ratio
    box_bumper = buttonBumper*4

    # Other colors
    global red_color, green_color, black_color, grey_color, drawColor
    red_color = [255, 0, 0]
    green_color = [0, 255, 0]
    black_color = [0, 0, 0]
    grey_color = '#808080'

    drawColor = black_color

    # Event Type
    global event_type, period, play_type, team, rink_flipped
    event_type = ""
    period = 0
    play_type = ""
    team = ""
    rink_flipped = False

    num_forward_lines = 5
    num_defense_lines = 4
    

    # Canvas
    global canvas, rink_img
    canvas = pygame.Surface(canvasSize)
    canvas.fill((255, 255, 255))
    rink_img = pygame.image.load(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png")).convert_alpha()
    rink_img = pygame.transform.scale(rink_img, canvasSize)
    canvas.blit(rink_img, (0,0))

    # Buttons and their respective functions.
    temp_button = None
        

    # Making the PERIOD Buttons
    period_buttons_list = []
    period_buttons = [
        ['1st Period', lambda: changePeriod(1, period_buttons_list)],
        ['2nd Period', lambda: changePeriod(2, period_buttons_list)],
        ['3rd Period', lambda: changePeriod(3, period_buttons_list)],
        ['OT', lambda: changePeriod(4, period_buttons_list)]
    ]
    # Text
    text_boxes.append(["Period", (screen_width - (len(period_buttons)*((buttonWidth*3)/4 + (buttonBumper*2))) + buttonBumper - buttonBumper*4, buttonBumper*3)])
    # Buttons
    for index, buttonDetails in enumerate(period_buttons):
        temp_button = GroupedButton((screen_width - (len(period_buttons)*((buttonWidth*3)/4 + (buttonBumper*2)))) + index * ((buttonWidth*3)/4 + buttonBumper) + buttonBumper*2, buttonBumper*3, (buttonWidth*3)/4, buttonHeight, font_size20, buttonDetails[0], buttonDetails[1])
        period_buttons_list.append(temp_button)
        objects.append(temp_button)
    
    # Making the Play Type Buttons
    play_type_buttons_list = []
    play_type_buttons = [
        ['5 on 5', lambda: changePlayType("5 on 5", play_type_buttons_list)],
        ['PP', lambda: changePlayType("PP", play_type_buttons_list)],
        ['PK', lambda: changePlayType("PK", play_type_buttons_list)]
    ]
    # Text
    text_boxes.append(["Play Type", (screen_width - (len(play_type_buttons)*(buttonWidth + (buttonBumper*2))) + buttonBumper - buttonBumper*7, buttonBumper*3 + buttonHeight + buttonBumper)])
    # Buttons
    for index, buttonDetails in enumerate(play_type_buttons):
        temp_button = GroupedButton((screen_width - (len(play_type_buttons)*(buttonWidth + (buttonBumper*2)))) + index * (buttonWidth + buttonBumper) + buttonBumper, buttonBumper*3 + (buttonHeight + buttonBumper), buttonWidth, buttonHeight, font_size20, buttonDetails[0], buttonDetails[1])
        play_type_buttons_list.append(temp_button)
        objects.append(temp_button)

    right_y_cord = buttonBumper*20

    # Making the COLOR Buttons
    color_buttons_list = []
    color_buttons = [
        ['Black', lambda: changeColor(canvas, black_color, color_buttons_list), grey_color],
        ['Red', lambda: changeColor(canvas, red_color, color_buttons_list), red_color],
        ['Green', lambda: changeColor(canvas, green_color, color_buttons_list), green_color]
    ]
    # Text
    text_boxes.append(["Color", (screen_width - (buttonWidth + (buttonBumper)*3), right_y_cord - buttonBumper*2)])
    # Buttons
    for index, buttonDetails in enumerate(color_buttons):
        temp_button = GroupedButton(screen_width - (buttonWidth + (buttonBumper)*3), index * (buttonHeight + buttonBumper) + right_y_cord, buttonWidth, buttonHeight, font_size20, buttonDetails[0], buttonDetails[1], buttonDetails[2])
        color_buttons_list.append(temp_button)
        objects.append(temp_button)
    
    # Making the EVENT Buttons
    event_buttons_x = screen_width - (buttonWidth + (buttonBumper)*3)*2
    event_buttons_list = []
    event_buttons = [
        ['Faceoff', lambda: changeEvent("Faceoff", event_buttons_list)],
        ['Pass', lambda: changeEvent("Pass", event_buttons_list)],
        ['Shot', lambda: changeEvent("Shot", event_buttons_list)],
        ['Goal', lambda: changeEvent("Goal", event_buttons_list)],
        ['1st Assist', lambda: changeEvent("1st Assist", event_buttons_list)],
        ['2nd Assist', lambda: changeEvent("2nd Assist", event_buttons_list)]
    ]
    # Text
    text_boxes.append(["Event", (event_buttons_x, right_y_cord - buttonBumper*2)])
    # Buttons
    for index, buttonDetails in enumerate(event_buttons):
        temp_button = GroupedButton(event_buttons_x,  index * (buttonHeight + buttonBumper) + right_y_cord, buttonWidth, buttonHeight, font_size20, buttonDetails[0], buttonDetails[1])
        event_buttons_list.append(temp_button)
        objects.append(temp_button)
    
    right_y_cord = right_y_cord + ((buttonHeight + buttonBumper) * len(event_buttons_list)) + buttonBumper*20


    # Making the Player Buttons
    global player_action_buttons
    global player_on_ice_buttons
    left_y_cord = buttonBumper*6
    player_action_buttons = []
    player_on_ice_buttons = []
    button_cords = []
    offset = + buttonWidth/3 + buttonBumper
    count = -1
    # forwards
    on_ice_functions = []
    for y in range(num_forward_lines):
         for x in range(3):
            count = count + 1
            # button cords
            button_cords.append([(x * (((buttonWidth/3 + buttonBumper) * 2) + buttonBumper*1.5)) + (buttonBumper*2), left_y_cord + (y * (buttonHeight + buttonBumper*3))])
            if full_player_roster[count] != '':
                # Text
                text_boxes.append([full_player_roster[count], ((x * (((buttonWidth/3 + buttonBumper) * 2) + buttonBumper*1.5)) + (buttonBumper*2), left_y_cord + (y * (buttonHeight + buttonBumper*3)) - buttonBumper*2)])
    
    # On Ice Buttons
    if full_player_roster[0] != '': player_on_ice_buttons.append(ToggleButton(button_cords[0][0], button_cords[0][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[0])))
    if full_player_roster[1] != '': player_on_ice_buttons.append(ToggleButton(button_cords[1][0], button_cords[1][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[1])))
    if full_player_roster[2] != '': player_on_ice_buttons.append(ToggleButton(button_cords[2][0], button_cords[2][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[2])))
    if full_player_roster[3] != '': player_on_ice_buttons.append(ToggleButton(button_cords[3][0], button_cords[3][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[3])))
    if full_player_roster[4] != '': player_on_ice_buttons.append(ToggleButton(button_cords[4][0], button_cords[4][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[4])))
    if full_player_roster[5] != '': player_on_ice_buttons.append(ToggleButton(button_cords[5][0], button_cords[5][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[5])))
    if full_player_roster[6] != '': player_on_ice_buttons.append(ToggleButton(button_cords[6][0], button_cords[6][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[6])))
    if full_player_roster[7] != '': player_on_ice_buttons.append(ToggleButton(button_cords[7][0], button_cords[7][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[7])))
    if full_player_roster[8] != '': player_on_ice_buttons.append(ToggleButton(button_cords[8][0], button_cords[8][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[8])))
    if full_player_roster[9] != '': player_on_ice_buttons.append(ToggleButton(button_cords[9][0], button_cords[9][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[9])))
    if full_player_roster[10] != '': player_on_ice_buttons.append(ToggleButton(button_cords[10][0], button_cords[10][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[10])))
    if full_player_roster[11] != '': player_on_ice_buttons.append(ToggleButton(button_cords[11][0], button_cords[11][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[11])))
    if full_player_roster[12] != '': player_on_ice_buttons.append(ToggleButton(button_cords[12][0], button_cords[12][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[12])))
    if full_player_roster[13] != '': player_on_ice_buttons.append(ToggleButton(button_cords[13][0], button_cords[13][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[13])))
    if full_player_roster[14] != '': player_on_ice_buttons.append(ToggleButton(button_cords[14][0], button_cords[14][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[14])))
    # Action Buttons
    if full_player_roster[0] != '': player_action_buttons.append(GroupedButton(button_cords[0][0] + offset, button_cords[0][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[0], player_action_buttons), full_player_roster[0]))
    if full_player_roster[1] != '': player_action_buttons.append(GroupedButton(button_cords[1][0] + offset, button_cords[1][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[1], player_action_buttons), full_player_roster[1]))
    if full_player_roster[2] != '': player_action_buttons.append(GroupedButton(button_cords[2][0] + offset, button_cords[2][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[2], player_action_buttons), full_player_roster[2]))
    if full_player_roster[3] != '': player_action_buttons.append(GroupedButton(button_cords[3][0] + offset, button_cords[3][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[3], player_action_buttons), full_player_roster[3]))
    if full_player_roster[4] != '': player_action_buttons.append(GroupedButton(button_cords[4][0] + offset, button_cords[4][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[4], player_action_buttons), full_player_roster[4]))
    if full_player_roster[5] != '': player_action_buttons.append(GroupedButton(button_cords[5][0] + offset, button_cords[5][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[5], player_action_buttons), full_player_roster[5]))
    if full_player_roster[6] != '': player_action_buttons.append(GroupedButton(button_cords[6][0] + offset, button_cords[6][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[6], player_action_buttons), full_player_roster[6]))
    if full_player_roster[7] != '': player_action_buttons.append(GroupedButton(button_cords[7][0] + offset, button_cords[7][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[7], player_action_buttons), full_player_roster[7]))
    if full_player_roster[8] != '': player_action_buttons.append(GroupedButton(button_cords[8][0] + offset, button_cords[8][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[8], player_action_buttons), full_player_roster[8]))
    if full_player_roster[9] != '': player_action_buttons.append(GroupedButton(button_cords[9][0] + offset, button_cords[9][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[9], player_action_buttons), full_player_roster[9]))
    if full_player_roster[10] != '': player_action_buttons.append(GroupedButton(button_cords[10][0] + offset, button_cords[10][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[10], player_action_buttons), full_player_roster[10]))
    if full_player_roster[11] != '': player_action_buttons.append(GroupedButton(button_cords[11][0] + offset, button_cords[11][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[11], player_action_buttons), full_player_roster[11]))
    if full_player_roster[12] != '': player_action_buttons.append(GroupedButton(button_cords[12][0] + offset, button_cords[12][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[12], player_action_buttons), full_player_roster[12]))
    if full_player_roster[13] != '': player_action_buttons.append(GroupedButton(button_cords[13][0] + offset, button_cords[13][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[13], player_action_buttons), full_player_roster[13]))
    if full_player_roster[14] != '': player_action_buttons.append(GroupedButton(button_cords[14][0] + offset, button_cords[14][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[14], player_action_buttons), full_player_roster[14]))
    
    left_y_cord = left_y_cord + (num_forward_lines * (buttonHeight + buttonBumper*3))
    button_cords = []
    # defense
    for y in range(num_defense_lines):
         for x in range(2):
            count = count + 1
            # on ice
            button_cords.append([(x * (((buttonWidth/3 + buttonBumper) * 2) + buttonBumper*1.5)) + (buttonBumper*8), left_y_cord + (y * (buttonHeight + buttonBumper*3))])
            if full_player_roster[count] != '':
                # Text
                text_boxes.append([full_player_roster[count], ((x * (((buttonWidth/3 + buttonBumper) * 2) + buttonBumper*1.5)) + (buttonBumper*8), left_y_cord + (y * (buttonHeight + buttonBumper*3)) - buttonBumper*2)])

    # On Ice Buttons
    if full_player_roster[15] != '': player_on_ice_buttons.append(ToggleButton(button_cords[0][0], button_cords[0][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[15])))
    if full_player_roster[16] != '': player_on_ice_buttons.append(ToggleButton(button_cords[1][0], button_cords[1][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[16])))
    if full_player_roster[17] != '': player_on_ice_buttons.append(ToggleButton(button_cords[2][0], button_cords[2][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[17])))
    if full_player_roster[18] != '': player_on_ice_buttons.append(ToggleButton(button_cords[3][0], button_cords[3][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[18])))
    if full_player_roster[19] != '': player_on_ice_buttons.append(ToggleButton(button_cords[4][0], button_cords[4][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[19])))
    if full_player_roster[20] != '': player_on_ice_buttons.append(ToggleButton(button_cords[5][0], button_cords[5][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[20])))
    if full_player_roster[21] != '': player_on_ice_buttons.append(ToggleButton(button_cords[6][0], button_cords[6][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[21])))
    if full_player_roster[22] != '': player_on_ice_buttons.append(ToggleButton(button_cords[7][0], button_cords[7][1], buttonWidth/3, buttonHeight, font_size20, "On Ice", lambda: addShift(full_player_roster[22])))
    # Action Buttons
    if full_player_roster[15] != '': player_action_buttons.append(GroupedButton(button_cords[0][0] + offset, button_cords[0][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[15], player_action_buttons), full_player_roster[15]))
    if full_player_roster[16] != '': player_action_buttons.append(GroupedButton(button_cords[1][0] + offset, button_cords[1][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[16], player_action_buttons), full_player_roster[16]))
    if full_player_roster[17] != '': player_action_buttons.append(GroupedButton(button_cords[2][0] + offset, button_cords[2][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[17], player_action_buttons), full_player_roster[17]))
    if full_player_roster[18] != '': player_action_buttons.append(GroupedButton(button_cords[3][0] + offset, button_cords[3][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[18], player_action_buttons), full_player_roster[18]))
    if full_player_roster[19] != '': player_action_buttons.append(GroupedButton(button_cords[4][0] + offset, button_cords[4][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[19], player_action_buttons), full_player_roster[19]))
    if full_player_roster[20] != '': player_action_buttons.append(GroupedButton(button_cords[5][0] + offset, button_cords[5][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[20], player_action_buttons), full_player_roster[20]))
    if full_player_roster[21] != '': player_action_buttons.append(GroupedButton(button_cords[6][0] + offset, button_cords[6][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[21], player_action_buttons), full_player_roster[21]))
    if full_player_roster[22] != '': player_action_buttons.append(GroupedButton(button_cords[7][0] + offset, button_cords[7][1], buttonWidth/3, buttonHeight, font_size20, "Action", lambda: changePlayerAction(full_player_roster[22], player_action_buttons), full_player_roster[22]))

    text_boxes.append([game_object.opponent.team_name, (buttonBumper*42, buttonBumper*12)])
    player_action_buttons.append(GroupedButton(buttonBumper*42, buttonBumper*14, buttonWidth, buttonHeight, font_size20, "Action", lambda: changePlayerAction(game_object.opponent.team_name, player_action_buttons), game_object.opponent.team_name))

    # add buttons to objects list
    for i in player_on_ice_buttons:
        objects.append(i)
    for i in player_action_buttons:
        objects.append(i)

    left_y_cord = left_y_cord + (num_defense_lines * (buttonHeight + buttonBumper*3))
    # goalies
    global goalie_in_net_buttons
    goalie_in_net_buttons = []
    for y in range(2):
        if goalies_names[y] != '':
            # Text
            text_boxes.append([goalies_names[y], (buttonBumper*14, left_y_cord + (y * (buttonHeight + buttonBumper*3)) - buttonBumper*2)])
            # Buttons
            temp_button = ToggleButton(buttonBumper*14, left_y_cord + (y * (buttonHeight + buttonBumper*3)), buttonWidth/2, buttonHeight, font_size20, "In Net")
            goalie_in_net_buttons.append(temp_button)
            objects.append(temp_button)

    
    top_buttons = [
        ['Save Event', lambda: saveEvent()],
        ['Clear', lambda: clearCanvas()],
        ['Flip Rink', lambda: flipCanvas()],
    ]
    # Making the buttons
    for index, buttonDetails in enumerate(top_buttons):
        temp_button = NormalButton((screen_width/2  - (len(top_buttons)/2*(buttonWidth + buttonBumper))) + (index * (buttonWidth + buttonBumper)), buttonBumper*3, buttonWidth, buttonHeight, font_size20, buttonDetails[0], buttonDetails[1])
        objects.append(temp_button)

    # Save Game button
    objects.append(NormalButton(screen_width - buttonBumper*3 - buttonWidth, screen_height - buttonBumper*3 - buttonHeight, buttonWidth, buttonHeight, font_size20, "Save Game Stats", lambda: saveGame(game_object)))

    # Display Stats buttons
    stat_buttons = [
        ['Show Faceoff Stats', lambda: displayFaceoff()],
        ['Show Game Stats', lambda: displayInGameStats()],
    ]
    # Making the buttons
    for index, buttonDetails in enumerate(stat_buttons):
        temp_button = NormalButton((screen_width/2  - (len(top_buttons)/2*(buttonWidth + buttonBumper))) + (index * (buttonWidth + buttonBumper)), buttonBumper*3 + buttonHeight + buttonBumper, buttonWidth, buttonHeight, font_size20, buttonDetails[0], buttonDetails[1])
        objects.append(temp_button)
    

    global quit
    quit = False

    # Game loop.
    while not quit:
        screen.fill((30, 30, 30))

        # Draw the Canvas at the center of the screen
        x, y = screen.get_size()
        # scaled_canvas = pygame.transform.smoothscale(canvas, (screen.get_size()[0]*(2/3), screen.get_size()[1]*(5/7)))
        # canvasSize = [scaled_canvas.get_size()[0], scaled_canvas.get_size()[1]]
        # screen.blit(scaled_canvas, ([x/2 - canvasSize[0]/2, y/2 - canvasSize[1]/2]))
        screen.blit(canvas, [x/2 - canvasSize[0]/2, y/2 - canvasSize[1]/2 + buttonBumper*6])

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

        # Drawing Text
        for text in text_boxes:
            screen.blit(pygame.font.SysFont('Arial', font_size18).render(text[0] + ':', False, (250, 250, 250)), text[1])
        
        # Drawing the Input Boxes
        # for box in input_boxes_list:
        #     box.rect.w = max(200*width_ratio, (box.txt_surface.get_width()+10))
        # for box in input_boxes_list:
        #     box.draw(screen)


        # Drawing with the mouse
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()

            # Calculate Position on the Canvas
            dx = mx - x/2 + canvasSize[0]/2
            dy = my - y/2 + canvasSize[1]/2 - buttonBumper*6

            pygame.draw.circle(
                canvas,
                drawColor,
                [dx, dy],
                brushSize,
            )

        pygame.display.flip()
        #fpsClock.tick(fps)
        fpsClock.tick()



if __name__ == "__main__":
    trackGameStats()