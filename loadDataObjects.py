import cv2
import os
import numpy as np
import pickle
import math # 'math' needed for 'sqrt'
from scipy import spatial
from datetime import date
import imageio
from PIL import Image as PImage
from PIL import ImageDraw, ImageFont
from os import path
import pygame
from visualizationHelpers import *



class Player_Stats():
    def __init__(self, number, name, position):
        self.number = number
        self.name = name
        self.position = position
        self.games_played = 0
        self.shifts = 0
        self.goals = 0
        self.assist = 0
        self.points = 0
        self.shots = 0
        self.shots_on_net = 0
        self.shots_high_danger = 0
        self.shots_map = None
        self.shots_time_graph = None
        self.shots_on_net_time_graph = None
        self.passes = 0
        self.passes_completed = 0
        self.passes_high_danger = 0
        self.passes_map = None
        self.passes_time_graph = None
        self.passes_completed_time_graph = None
        self.passes_zone_percent_time_graph = None
        #self.corsi = 0
        #self.plus_minus = 0
        self.faceoffs_taken = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.faceoffs_won = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.faceoff_d_percent = 0
        self.faceoff_n_percent = 0
        self.faceoff_o_percent = 0
        self.faceoff_left_percent = 0
        self.faceoff_right_percent = 0
        self.faceoff_total_percent = 0
        self.faceoff_map = None
        self.faceoff_time_graph = None
        self.faceoff_detailed_time_graph = None
        # Goalie Stats
        self.gaa = 0
        self.sv_percent = 0
        self.sv_per_game = 0
        self.save_percent_time_graph = None
        self.goals_against_time_graph = None



    def calculateAllStats(self, opponents, shots_by_game_data, goals_by_game_data, pass_by_game_data, assist_by_game_data, faceoff_by_game_data, shifts_by_game_data):

        # Games Played
        games_played = len(opponents)
        self.games_played = len(opponents)
            
        if games_played > 0:
            # Shots
            shot_count = 0
            on_net_count = 0
            high_danger_count = 0
            all_shot_data = []
            for game in shots_by_game_data:
                for shot in game:
                    all_shot_data.append(shot)
                    if shot.on_net:
                        on_net_count = on_net_count + 1
                    if shot.high_danger:
                        high_danger_count = high_danger_count + 1
            shot_count = len(all_shot_data)

            # Goals
            goal_count = 0
            all_goals_data = []
            for game in goals_by_game_data:
                for goal in game:
                    all_goals_data.append(goal)
            goal_count = len(all_goals_data)

            if all_shot_data != []:
                if self.name == "Opposing Team" or self.position == "G":
                    self.shots_map = shotlocationmap1point(all_shot_data, all_goals_data, True)
                else:
                    self.shots_map = shotlocationmap1point(all_shot_data, all_goals_data, False)
                if games_played > 1:
                    self.shots_time_graph, self.shots_on_net_time_graph = shotsTimeGraph(shots_by_game_data, opponents)

            self.shots = shot_count
            self.goals = goal_count
            self.shots_on_net = on_net_count
            self.shots_high_danger = high_danger_count
            
            

            # Goalie Specific Stats
            if self.position == "G":
                save_percent_data_by_game = []
                goals_against_by_game = []
                for game in range(len(shots_by_game_data)):
                    if len(shots_by_game_data[game]) != 0:
                            save_percent_data_by_game.append(round(1-(len(goals_by_game_data[game])/len(shots_by_game_data[game])), 2))
                    else:
                        save_percent_data_by_game.append(0)
                        games_played = games_played - 1
                    goals_against_by_game.append(len(goals_by_game_data[game]))
                
                self.games_played = games_played
                if games_played != 0:
                    self.gaa = round(goal_count / games_played, 2)
                    self.sv_per_game = round((shot_count - goal_count) / games_played, 2)
                if shot_count != 0:
                    self.sv_percent = round(1 - (goal_count / shot_count), 2)
                if games_played > 1:
                    self.save_percent_time_graph = single_fig_line(save_percent_data_by_game, opponents, "Save Percentage per Game", "Games", "Save Percent")
                    self.goals_against_time_graph = single_fig_line(goals_against_by_game, opponents, "Goals Against per Game", "Games", "Goals Against")
                


            pass_count = 0
            assist_count = 0
            complete_count = 0
            high_danger_count = 0
            all_pass_data = []
            all_assist_data = []
            if self.name != "Opposing Team" or self.position == "G":  # Player Stats
                # Passes
                for game in pass_by_game_data:
                    for Pass in game:
                        all_pass_data.append(Pass)
                        if Pass.complete:
                            complete_count = complete_count + 1
                        if Pass.high_danger:
                            high_danger_count = high_danger_count + 1
                pass_count = len(all_pass_data)

                # Assist
                for game in assist_by_game_data:
                    for assist in game:
                        all_assist_data.append(assist)
                assist_count = len(all_assist_data)

                if all_pass_data != []:
                    self.passes_map = passlocationmap2point(all_pass_data, all_assist_data)
                    if games_played > 1:
                        self.passes_time_graph, self.passes_completed_time_graph, self.passes_zone_percent_time_graph = passTimeGraph(pass_by_game_data, opponents)

                self.passes = pass_count
                self.passes_completed = complete_count
                self.passes_high_danger = high_danger_count
                self.assist = assist_count
                
            if self.name == "Saul Drantch":
                pass

            all_faceoff_data = []
            zone_data_by_game = []
            total_zone_data = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]    # [won, taken]
            faceoff_count = 0
            total_win_count = 0
            if self.name != "Opposing Team" or self.position == "G":  # Player Stats
                # Faceoffs
                for game in faceoff_by_game_data:
                    zone_data = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]    # [won, taken]
                    for faceoff in game:
                        all_faceoff_data.append(faceoff)
                        faceoff_count = faceoff_count + 1
                        zone_data[faceoff.zone][1] = zone_data[faceoff.zone][1] + 1
                        total_zone_data[faceoff.zone][1] = total_zone_data[faceoff.zone][1] + 1
                        if faceoff.win:
                            total_win_count = total_win_count + 1
                            zone_data[faceoff.zone][0] = zone_data[faceoff.zone][0] + 1
                            total_zone_data[faceoff.zone][0] = total_zone_data[faceoff.zone][0] + 1
                    zone_data_by_game.append(zone_data)

                if all_faceoff_data != []:
                    self.faceoff_d_percent, self.faceoff_n_percent, self.faceoff_o_percent, self.faceoff_left_percent, self.faceoff_right_percent = getFaceoffAreaPercents(total_zone_data)
                    self.faceoff_total_percent = round((total_win_count/faceoff_count)*100, 2)
                    self.faceoff_map = faceoffMap(total_zone_data)
                    if games_played > 1:
                        self.faceoff_time_graph, self.faceoff_detailed_time_graph = faceoffTimeGraph(zone_data_by_game, opponents)
                
                for game in zone_data_by_game:
                    for zone in range(len(game)):
                        self.faceoffs_won[zone] = self.faceoffs_won[zone] + game[zone][0]
                        self.faceoffs_taken[zone] = self.faceoffs_taken[zone] + game[zone][1]
            
            

            # Shifts
            if self.name != "Opposing Team" or self.position == "G":  # Player Stats
                for num in shifts_by_game_data:
                    self.shifts = self.shifts + num
        


        return
    
    

    

class Goalie():
    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.games_played = 0
        self.shots_against = 0
        self.goals_against = 0
        self.save_percent = 0
        self.gaa = 0






# TESTING
if __name__ == "__main__":
    folder_name = "test"
    directory = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/' + folder_name + '/'
    filename = "46_pass_0.png"
    text = filename.split('_')[1]
    print(text)
    img = cv2.imread(directory + filename)
    pass

    # obj = MyClass(10)
    # save_object(obj, filename)

    # obj = load_object(filename)