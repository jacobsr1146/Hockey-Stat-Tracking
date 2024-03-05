import sys
import pygame
import ctypes
import os
import math
from os import path
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from helpers import NormalButton
from helpers import GroupedButton
from helpers import ToggleButton
from helpers import InputBox
from helpers import OptionBox
from visualizationHelpers import *
from loadDataObjects import *
from MakeReport import *

player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
#player_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
#game_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
roster_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/rosters/'
#roster_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/rosters/'


def findActivePlayerButton():
    if player_option_box.selected == 0:
        return None
    else:
        return player_option_box.option_list[player_option_box.selected]

def getAllPlayerObjects(game_objects, name):
    player_game_objects = []
    for game in game_objects:
        player_game_objects.append(game.our_team.getPlayerObj(name))
    return player_game_objects

def getAllPlayerOpponents(game_objects, name):
    opponents = []
    for game in game_objects:
        if game.our_team.getPlayerObj(name) != None:
            opponents.append(game.date + " " + game.opponent.team_name)
    return opponents


def getAllGameOpponents(game_objects):
    opponents = []
    for game in game_objects:
            opponents.append(game.date + " " + game.opponent.team_name)
    return opponents

def ShotVisualizations(player):
    global current_stats, stat_images, stat_text_boxes, canvas
    stat_images = []
    stat_text_boxes = []
    current_stats = "shots"
    canvas.fill((255, 255, 255))

    if player.position == "G":
        GoalieVisualizations(player)
        return
    
    stat_text_boxes.append([player.name + "  |  Shooting Data", (10, 10), 46])
    
    stat_text_boxes.append(["Goals: " + str(player.goals), (50, 50 + 40*1), 32])
    stat_text_boxes.append(["Shots: " + str(player.shots), (50, 50 + 40*2), 32])
    if player.shots != 0:
        stat_text_boxes.append(["On Net Percent: " + str(round((player.shots_on_net/player.shots)*100, 2)) + "%", (50, 50 + 40*3), 32])
        stat_text_boxes.append(["High Danger Shot Percent: " + str(round((player.shots_high_danger/player.shots)*100, 2)) + "%", (50, 50 + 40*4), 32])
    else:
        stat_text_boxes.append(["On Net Percent: 0%", (50, 50 + 40*3), 32])
        stat_text_boxes.append(["High Danger Shot Percent: 0%", (50, 50 + 40*4), 32])
    
    stat_images.append([player.shots_map, (50, 430)])
    stat_images.append([player.shots_time_graph, (canvas.get_width()/2 - 10, 50)])
    stat_images.append([player.shots_on_net_time_graph, (canvas.get_width()/2 - 10, 550)])

    #stat_text_boxes.append(["No Shooting Data Available", (canvas.get_width()/2 - 50, canvas.get_height()/2), 32])
        
    

    # BLIT IMAGE OF ALL STATS TO THE SCREEN'S CANVAS
    return

def PassVisualizations(player):
    global current_stats, stat_images, stat_text_boxes, canvas
    stat_images = []
    stat_text_boxes = []
    current_stats = "pass"
    canvas.fill((255, 255, 255))
    
    stat_text_boxes.append([player.name + "  |  Passing Data", (10, 10), 46])

    if player.name == "Opposing Team" or player.position == "G":
        stat_text_boxes.append(["No Passing Data Available", (canvas.get_width()/2 - 50, canvas.get_height()/2), 32])
    else:
        stat_text_boxes.append(["Assist: " + str(player.assist), (50, 50 + 40*1), 32])
        stat_text_boxes.append(["Passes: " + str(player.passes), (50, 50 + 40*2), 32])
        if player.passes != 0:
            stat_text_boxes.append(["Total Completion Percent: " + str(round((player.passes_completed/player.passes)*100, 2)) + "%", (50, 50 + 40*3), 32])
            stat_text_boxes.append(["High Danger Pass Percent: " + str(round((player.passes_high_danger/player.passes)*100, 2)) + "%", (50, 50 + 40*4), 32])
        else:
            stat_text_boxes.append(["Total Completion Percent: 0%", (50, 50 + 40*3), 32])
            stat_text_boxes.append(["High Danger Pass Percent: 0%", (50, 50 + 40*4), 32])
        stat_images.append([player.passes_map, (50, 430)])
        #stat_images.append([all_passes_time_graph, (canvas.get_width()/2 - 10, 50)])
        stat_images.append([player.passes_completed_time_graph, (canvas.get_width()/2 - 10, 50)])
        stat_images.append([player.passes_zone_percent_time_graph, (canvas.get_width()/2 - 10, 550)])
        
    #stat_text_boxes.append(["No Passing Data Available", (canvas.get_width()/2 - 50, canvas.get_height()/2), 32])

    # BLIT IMAGE OF ALL STATS TO THE SCREEN'S CANVAS
    return

def FaceoffVisualizations(player):
    global current_stats, stat_images, stat_text_boxes, canvas
    stat_images = []
    stat_text_boxes = []
    current_stats = "faceoffs"
    canvas.fill((255, 255, 255))
    
    stat_text_boxes.append([player.name + "  |  Faceoff Data", (10, 10), 46])

    if player.name == "Opposing Team" or player.position == "G":
        stat_text_boxes.append(["No Faceoff Data Available", (canvas.get_width()/2 - 50, canvas.get_height()/2), 32])
    else:
        stat_text_boxes.append(["Total Completion Percent: " + str(player.faceoff_total_percent) + "%", (50, 50 + 40), 40])
        stat_text_boxes.append(["Offensive Faceoffs: " + str(player.faceoff_o_percent) + "%", (80, 70 + 40*2), 32])
        stat_text_boxes.append(["Netural Zone Faceoffs: " + str(player.faceoff_n_percent) + "%", (80, 70 + 40*3), 32])
        stat_text_boxes.append(["Defensive Faceoffs: " + str(player.faceoff_d_percent) + "%", (80, 70 + 40*4), 32])
        stat_text_boxes.append(["Left Side Faceoffs: " + str(player.faceoff_left_percent) + "%", (80, 70 + 40*5), 32])
        stat_text_boxes.append(["Right Side Faceoffs: " + str(player.faceoff_right_percent) + "%", (80, 70 + 40*6), 32])
        stat_images.append([player.faceoff_map, (50, 460)])
        stat_images.append([player.faceoff_time_graph, (canvas.get_width()/2 - 10, 50)])
        stat_images.append([player.faceoff_detailed_time_graph, (canvas.get_width()/2 - 10, 550)])

    # BLIT IMAGE OF ALL STATS TO THE SCREEN'S CANVAS
    return

def GoalieVisualizations(player):
    global current_stats, stat_images, stat_text_boxes, canvas
    stat_images = []
    stat_text_boxes = []
    # current_stats = "goalie"
    canvas.fill((255, 255, 255))
    
    stat_text_boxes.append([player.name + "  |  Goalie Data", (10, 10), 46])

    if player.name == "Opposing Team" or player.position != "G":
        stat_text_boxes.append(["No Goalie Data Available", (canvas.get_width()/2 - 50, canvas.get_height()/2), 32])
    else:
        stat_text_boxes.append(["GAA: " + str(player.gaa), (50, 50 + 40*1), 32])
        stat_text_boxes.append(["Save Percentage: " + str(player.sv_percent) + "%", (50, 50 + 40*2), 32])
        stat_text_boxes.append(["Saves per Game: " + str(player.sv_per_game), (50, 50 + 40*3), 32])
        stat_images.append([player.shots_map, (50, 430)])
        stat_images.append([player.save_percent_time_graph, (canvas.get_width()/2 - 10, 50)])
        stat_images.append([player.goals_against_time_graph, (canvas.get_width()/2 - 10, 550)])

    # BLIT IMAGE OF ALL STATS TO THE SCREEN'S CANVAS
    return

def LeaderboardVisualizations():
    global current_stats, stat_images, stat_text_boxes, canvas, canvas_pos,  width_ratio, height_ratio, screen
    stat_images = []
    stat_text_boxes = []
    current_stats = "leaderboards"
    canvas.fill((255, 255, 255))

    selected_stat = leader_option_box.option_list[leader_option_box.selected]
    stat_text_boxes.append(["Team Leaderboards | " + selected_stat, (10, 10), 46])

    player_names = []
    goals = []
    points = []
    assists = []
    shots = []
    shots_on_net_percent = []
    shifts = []
    corsi = []
    passes = []
    passing_percent = []
    

    return


def displayStats(list_player_objects):

    name = player_option_box.option_list[player_option_box.selected]
    player = None
    for player_obj in list_player_objects:
        if player_obj.name == name:
            player = player_obj
    if player == None:
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Player Error','No Player Selected')
        return
    

    current_stats = stat_option_box.option_list[stat_option_box.selected]
    # If a Data button was already pressed, show that data
    if current_stats == "Shooting":
        ShotVisualizations(player)
    elif current_stats == "Passing":
        PassVisualizations(player)
    elif current_stats == "Faceoffs":
        FaceoffVisualizations(player)
    # elif current_stats == "leaderboards":
    #     LeaderboardVisualizations(game_objects)
    else:
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Stat Error','No Stat Selected')
        return

def printStats(list_player_objects):
    name = player_option_box.option_list[player_option_box.selected]
    player = None
    for player_obj in list_player_objects:
        if player_obj.name == name:
            player = player_obj
    if player == None:
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Player Error','No Player Selected')
        return

    current_stats = stat_option_box.option_list[stat_option_box.selected]
    if current_stats == "None":
        Tk().wm_withdraw() #to hide the main window
        messagebox.showinfo('Stat Error','Stat Selected')
        return
    
    makeReport(player, current_stats)

    return

def printAll(list_player_objects):
    for player in list_player_objects:
        makeReport(player, "All")
    
    return

def forceQuit():
    global quit
    quit = True


def getStats():
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
    global width_ratio, height_ratio, screen
    width_ratio = info.current_w/scaled_w
    height_ratio = info.current_h/scaled_h
    screen_width,screen_height = info.current_w - 10*width_ratio, info.current_h - 60*height_ratio
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    # Drawing Area Size
    global canvasSize
    #canvasSize = [1260, 760]
    canvasSize = [1375*width_ratio, 855*height_ratio]

    # Variables

    # font size
    font_size18 = int(18 * height_ratio)
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
    buttonWidth = 200*width_ratio
    buttonHeight = 75*height_ratio
    buttonBumper = 10*width_ratio

    # Input Boxes Variables
    box_width = 140*width_ratio
    box_height = 32*height_ratio
    box_bumper = buttonBumper*4

    option_box_width = 290*width_ratio
    option_box_height = 90*height_ratio

    option_boxes = []

    list_player_objects = []

    # get all game objects
    tk.Tk().withdraw() # part of the import if you are not using other tkinter functions
    fn = askopenfilenames()
    game_objects = []
    for file in fn:
        game_objects.append(load_object(file))
    
    opponents = getAllGameOpponents(game_objects)
    
    # create and load player objects from the game objects
    player_database = open(player_path + 'player database.txt')
    for line in player_database:
        player_num = line.split(", ")[0]
        name = line.split(", ")[1]
        position = line.split(", ")[2][:-1]
        player_object = Player_Stats(player_num, name, position)
        player_game_objects = getAllPlayerObjects(game_objects, name)
        player_opponents = getAllPlayerOpponents(game_objects, name)
        all_goal_data = []
        all_shot_data = []
        all_assist_data = []
        all_pass_data = []
        all_faceoff_data = []
        all_shifts_data = []
        for player in player_game_objects:
            if player != None:
                # Check for goalie
                if player.position == "Starter" or player.position == "Backup":
                    all_shot_data.append(player.shots_against)
                    all_goal_data.append(player.goals_against)
                else:
                    all_shot_data.append(player.shots)
                    all_goal_data.append(player.goals)
                    all_pass_data.append(player.passes)
                    all_assist_data.append(player.assists)
                    all_faceoff_data.append(player.faceoffs)
                    all_shifts_data.append(player.shifts)
            else:
                if position == "G":
                    all_shot_data.append([])
                    all_goal_data.append([])
        
        player_object.calculateAllStats(player_opponents, all_shot_data, all_goal_data, all_pass_data, all_assist_data, all_faceoff_data, all_shifts_data)

        list_player_objects.append(player_object)


    # Team data
    for game in game_objects:
        # OUR TEAM DATA
        all_shot_data = []
        all_goal_data = []
        all_pass_data = []
        all_faceoff_data = []
        all_shot_data.append(game.our_team.shots)
        all_goal_data.append(game.our_team.goals)
        all_pass_data.append(game.our_team.passes)
        all_faceoff_data.append(game.our_team.faceoffs)

    for game in game_objects:
        # OPPOSING TEAM DATA
        all_shot_data = []
        all_goal_data = []
        all_shot_data.append(game.opponent.shots)
        all_goal_data.append(game.opponent.goals)


    global current_stats
    current_stats = ""

    # Buttons and their respective functions.
    player_names = []
    player_database = open(player_path + 'player database.txt')
    for line in player_database:
        name = line.split(", ")[1]
        player_names.append(name)

    player_names = sorted(player_names)



    text_boxes = []
    

    # Option Boxes

    global leader_option_box
    stat_options = ["Goals", "Assist", "Points", "Shots", "Shot %", "HD Shot %", "Passes", "Passing %", "HD_Passing %", "Shifts", "Corsi", "+/-", "Faceoff %"]
    leader_option_box = OptionBox(buttonBumper*3, buttonBumper*5 + (buttonHeight + buttonBumper*3)*5, buttonWidth, buttonHeight, stat_options)
    option_boxes.append(leader_option_box)
    text_boxes.append(["Leaderboard Stats", (buttonBumper*3, buttonBumper*5 + (buttonHeight + buttonBumper*3)*5 - buttonBumper*2), int(22*width_ratio)])
    
    global player_option_box
    player_options = ["-"] + player_names
    player_option_box = OptionBox(buttonBumper*3, buttonBumper*5 + (buttonHeight + buttonBumper*3)*1, buttonWidth, buttonHeight, player_options, font_size18)
    option_boxes.append(player_option_box)
    text_boxes.append(["Select Player", (buttonBumper*3, buttonBumper*5 + (buttonHeight + buttonBumper*3)*1 - buttonBumper*2), int(22*width_ratio)])

    global stat_option_box
    stat_options = ["-", "Shooting", "Passing", "Faceoffs"]
    stat_option_box = OptionBox(buttonBumper*3 + (buttonWidth + buttonBumper)*1, buttonBumper*5 + (buttonHeight + buttonBumper*3)*1, buttonWidth, buttonHeight, stat_options, font_size18)
    option_boxes.append(stat_option_box)
    text_boxes.append(["Select Data", (buttonBumper*3 + (buttonWidth + buttonBumper)*1, buttonBumper*5 + (buttonHeight + buttonBumper*3)*1 - buttonBumper*2), int(22*width_ratio)])
    
    
    # Buttons

    # Get Stats Button
    objects.append(NormalButton(buttonBumper*3, buttonBumper*5 + (buttonHeight + buttonBumper*3)*0, buttonWidth, buttonHeight, font_size18, "Get Data", lambda: displayStats(list_player_objects)))

    # Print Stats Button
    objects.append(NormalButton(buttonBumper*4 + buttonWidth, buttonBumper*5 + (buttonHeight + buttonBumper*3)*0, buttonWidth, buttonHeight, font_size18, "Print Stats", lambda: printStats(list_player_objects)))

    # Leaderboard Button
    objects.append(NormalButton(buttonBumper*3, buttonBumper*5 + (buttonHeight + buttonBumper*3)*4, buttonWidth, buttonHeight, font_size18, "Get Data", lambda: LeaderboardVisualizations()))

    # Back Button
    objects.append(NormalButton(screen_width - buttonWidth/2 - buttonBumper*4, buttonBumper, buttonWidth/2, buttonHeight/2, font_size18, '<---', lambda: forceQuit()))

    # Print All Button
    objects.append(NormalButton(screen_width - buttonWidth/2 - buttonBumper*4, buttonBumper*2 + buttonHeight, buttonWidth/2, buttonHeight/2, font_size18, 'Print All', lambda: printAll(list_player_objects)))

    
    # Making the STAT items
    global stat_images, stat_text_boxes
    stat_images = []
    stat_text_boxes = []

    

    # Canvas
    global canvas, screen_img
    canvas = pygame.Surface(canvasSize)
    canvas.fill((255, 255, 255))
    # screen_img = pygame.image.load(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png")).convert_alpha()
    # screen_img = pygame.transform.scale(screen_img, canvasSize)
    # canvas.blit(screen_img, (0,0))

    global quit
    quit = False
    global canvas_pos

    # Game loop.
    while not quit:
        screen.fill((30, 30, 30))

        # Draw the Canvas at the center of the screen
        x, y = screen.get_size()
        # scaled_canvas = pygame.transform.smoothscale(canvas, (screen.get_size()[0]*(2/3), screen.get_size()[1]*(5/7)))
        # canvasSize = [scaled_canvas.get_size()[0], scaled_canvas.get_size()[1]]
        # screen.blit(scaled_canvas, ([x/2 - canvasSize[0]/2, y/2 - canvasSize[1]/2]))
        canvas_pos = [3 * (((buttonWidth/3 + buttonBumper) * 2) + buttonBumper*1.5), (buttonHeight + (buttonBumper*6))]
        screen.blit(canvas, canvas_pos)

        event_list = pygame.event.get()
        for event in event_list:
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
            screen.blit(pygame.font.SysFont('Arial', text[2]).render(text[0] + ':', False, (250, 250, 250)), text[1])
        
        # Drawing the Input Boxes
        # for box in input_boxes_list:
        #     box.update()
        # for box in input_boxes_list:
        #     box.draw(screen)

        # Drawing Option Boxes
        # for box in option_boxes:
        #     box.draw(screen)
        #     selected_option = box.update(event_list)
        #     if selected_option >= 0:
        #         LeaderboardVisualizations(game_objects, stat_options[selected_option])
        #         print(selected_option)


        # Stat Specific Stuff

        # Drawing Text
        for text in stat_text_boxes:
            canvas.blit(pygame.font.SysFont('Arial', int(text[2]*height_ratio)).render(text[0], False, (0, 0, 0)), (text[1][0]*width_ratio, text[1][1]*height_ratio))
        
        # Drawing Images
        for image in stat_images:
            if image[0] != None:
                canvas.blit(image[0], image[1])
        
        # Drawing Option Boxes
        for box in option_boxes:
            box.draw(screen)
            selected_option = box.update(event_list)



        pygame.display.flip()
        #fpsClock.tick(fps)
        fpsClock.tick()
    
    return


if __name__ == "__main__":
    getStats()