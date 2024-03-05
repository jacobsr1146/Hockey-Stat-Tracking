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
import numpy as np
from numpy import asarray
from extractData import *

player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
img_dir = path.join(path.dirname(__file__), 'img')

map_offset_x = 160
map_offset_y = 50

red_color = (255, 0, 0)
green_color = (0, 255, 0)
black_color = (0, 0, 0)
grey_color = '#808080'

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
    image.show()

    # Save
    #cv2.imwrite("result.png", image)

    return


# time_frame_flags = ['Game Stats', 'Month Stats', 'Season Stats']
# data_type_flags = ['All Player Stats', 'Team Stats']
# stat_type_flags = ['All Stats', 'Shots', 'Passes', 'Goals', 'Assists', '+/-', 'Faceoffs']
# game_play_type_flags = ["5v5", "Power Play", "Penalty Kill"]
def createVisualizations(time_frame_flags, data_type_flags, stat_type_flags, game_play_type_flags):
    game_stats_flag = time_frame_flags[0]
    month_stats_flag = time_frame_flags[1]
    season_stats_flag = time_frame_flags[2]
    player_stats_flag = data_type_flags[0]
    team_stats_flag = data_type_flags[1]
    all_events_flag = stat_type_flags[0]
    if all_events_flag:
        shots_flag = True
        passes_flag = True
        goals_flag = True
        assist_flag = True
        plusminus_flag = True
        faceoffs_flag = True
    else:
        shots_flag = stat_type_flags[1]
        passes_flag = stat_type_flags[2]
        goals_flag = stat_type_flags[3]
        assist_flag = stat_type_flags[4]
        plusminus_flag = stat_type_flags[5]
        faceoffs_flag = stat_type_flags[6]
    ES_flag = game_play_type_flags[0]
    PP_flag = game_play_type_flags[1]
    PK_flag = game_play_type_flags[2]

    if player_stats_flag:   # Player Stats
        for i in range(len(time_frame_flags)-1):
            if i == 0 and time_frame_flags[i]:  # Last Game Stats
                time_frame = "game"
            elif i == 1 and time_frame_flags[i]:  # Last Month Stats
                time_frame = "month"
            elif i == 2 and time_frame_flags[i]:  # Season Stats
                time_frame = "season"
            
            # Go through each player object
            for file in os.listdir(player_path):
                filename = os.fsdecode(file)
                if not filename.endswith(".txt"): 
                    my_file = Path(player_path + '/' + filename)
                    player_object = load_object(my_file)
                    shot_list = []
                    pass_list = []
                    goal_list = []
                    assist_list = []
                    faceoff_list = []
                    plusminus = 0
                    if shots_flag:
                        #shot_list = player_object.getShots(time_frame, ES_flag, PP_flag, PK_flag)
                        shot_list = player_object.getShots("season", ES_flag, PP_flag, PK_flag)
                        if shot_list != []:
                            # Get list of shots on net and high danger
                            on_net_shot_list = []
                            high_danger_shot_list = []
                            for shot in shot_list:
                                if shot.on_net:
                                    on_net_shot_list.append(shot)
                                if shot.high_danger:
                                    high_danger_shot_list.append(shot)

                    if passes_flag:
                        pass_list = player_object.getPasses(time_frame, ES_flag, PP_flag, PK_flag)
                        if pass_list != [[], [], []]:
                            # Get list of passes completed/missed and high danger
                            # zones = [D-Zone, Neutral-Zone, O-Zone]
                            completed_pass_list = [[], [], []]
                            missed_pass_list = [[], [], []]
                            high_danger_pass_list = []
                            for zone in range(len(pass_list)-1):
                                for Pass in pass_list[zone]:
                                    if Pass.completed:
                                        completed_pass_list[zone].append(Pass)
                                        if Pass.high_danger:
                                            high_danger_pass_list.append(Pass)
                                    else:
                                        missed_pass_list[zone].append(Pass)
                    if goals_flag:
                        goal_list = player_object.getGoals(time_frame, ES_flag, PP_flag, PK_flag)
                    if assist_flag:
                        assist_list = player_object.getAssists(time_frame, ES_flag, PP_flag, PK_flag)
                        if assist_list != []:
                            # Get list of shots on net
                            assist1_list = []
                            assist2_list = []
                            for assist in assist_list:
                                if assist.type == 1:
                                    assist1_list.append(assist)
                                else:
                                    assist2_list.append(assist)
                    if faceoffs_flag:
                        faceoff_list = player_object.getFaceoffs(time_frame, ES_flag, PP_flag, PK_flag)
                    if plusminus_flag:
                        filename = "Boulder_stats"
                        my_file = Path(team_path + '/' + filename)
                        team_object = load_object(my_file)
                        goals_for = team_object.getPlayerPlusMinus(player_object.number, time_frame, ES_flag, PP_flag, PK_flag) # get goals for
                        goals_against = 0
                        for file in os.listdir(team_path):  # go through every opposing team's stats object
                            filename = os.fsdecode(file)
                            if filename != "Boulder_stats": 
                                my_file = Path(team_path + '/' + filename)
                                team_object = load_object(my_file)
                                goals_against = goals_against + team_object.getPlayerPlusMinus(player_object.number, time_frame, ES_flag, PP_flag, PK_flag) # get goals against

                    # Now that we have all the needed data, we need to visualize it
                    # SHOT
                    shots_heatmap_all = locationmap1point(shot_list)
                    shots_heatmap_on_net = locationmap1point(on_net_shot_list)
                    shot_on_net_percent = len(on_net_shot_list)/len(shot_list)
                    shot_high_danger_percent = len(high_danger_shot_list)/len(shot_list)
                    # PASS
                    # pass_heatmap_completed = heatmap2points(completed_pass_list)
                    # pass_heatmap_missed = heatmap2points(missed_pass_list)
                    # pass_all_completed_percent = 100*(len(completed_pass_list[0]) + len(completed_pass_list[1]) + len(completed_pass_list[2]))/(len(pass_list[0]) + len(pass_list[1]) + len(pass_list[2]))
                    # pass_d_zone_completed_percent = 100*len(completed_pass_list[0])/len(pass_list[0])
                    # pass_n_zone_completed_percent = 100*len(completed_pass_list[1])/len(pass_list[1])
                    # pass_o_zone_completed_percent = 100*len(completed_pass_list[2])/len(pass_list[2])
                    # pass_high_danger_percent = 100*len(high_danger_pass_list)/(len(pass_list[0]) + len(pass_list[1]) + len(pass_list[2]))
                    # # GOAL
                    # goal_heatmap = heatmap1point(goal_list)
                    # goal_count = len(goal_list)
                    # # ASSIST
                    # assist_heatmap_all = heatmap1point(assist_list)
                    # assist_heatmap_1st = heatmap1point(assist1_list)
                    # assist_heatmap_2nd = heatmap1point(assist2_list)
                    # assist_count = len(assist_list)
                    # assist1_count = len(assist1_list)
                    # assist2_count = len(assist2_list)
                    # # FACEOFF
                    # faceoff_map = createFaceoffMap(faceoff_list)
                    # # PLUSMINUS
                    # plusminus = goals_for - goals_against




    else:   # Team Stats
        pass

    

    return




# time_frame_flags = ['Game Stats', 'Month Stats', 'Season Stats']
# data_type_flags = ['All Player Stats', 'Team Stats']
# stat_type_flags = ['All Stats', 'Shots', 'Passes', 'Goals', 'Assists', '+/-', 'Faceoffs']
# game_play_type_flags = ["5v5", "Power Play", "Penalty Kill"]
if __name__ == "__main__":
    time_frame_flags = [True, False, False]
    data_type_flags = [True, False]
    stat_type_flags = [False, True, False, False, False, False, False]
    game_play_type_flags = [True, False, False]
    createVisualizations(time_frame_flags, data_type_flags, stat_type_flags, game_play_type_flags)