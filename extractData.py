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

def getLastDate(list):
    last_date = None
    for item in list:
        if last_date == None:
            last_date = item.date
        elif item.date > last_date:
            last_date = item.date
    return last_date

# Bubble Sort
def sortByDate(list):
    temp_item = None
    change = True
    while change:
        change = False
        for i in range(len(list)-2):
            if list[i].date < list[i+1].date:
                change = True
                temp_item = list[i]
                list[i] = list[i+1]
                list[i+1] = temp_item
    return list


class Game():
    def __init__(self, our_team_name, opponent_name, date, forward_lineup, defense_lineup, goalies):
        self.our_team = Team(our_team_name, forward_lineup, defense_lineup, goalies)
        self.opponent = Team(opponent_name)
        self.date = date


class Team():
    def __init__(self, team_name, forward_lineup = None, defense_lineup = None, goalies = None):
        self.team_name = team_name
        self.forward_lines = forward_lineup # list of ForwardLine objects
        self.defense_lines = defense_lineup # list of DefenseLine objects
        self.goalies = goalies # list of Goalie objects
        self.shots = []
        self.passes = []
        self.goals = []
        self.assists = []
        self.faceoffs = []
    
    def getPlayerObj(self, player_name):
        player_object = None
        for line in self.forward_lines:
            if line.LW != None:
                if line.LW.name == player_name:
                    player_object = line.LW
            if line.C != None:
                if line.C.name == player_name:
                    player_object = line.C
            if line.RW != None:
                if line.RW.name == player_name:
                    player_object = line.RW
        for line in self.defense_lines:
            if line.LD!=None:
                if line.LD.name == player_name:
                    player_object = line.LD
            if line.RD != None:
                if line.RD.name == player_name:
                    player_object = line.RD
        for goalie in self.goalies:
            if goalie != None:
                if goalie.name == player_name:
                    player_object = goalie
        return player_object
    
    def addPass(self, action, player_name=None):
        # update team action
        self.passes.append(action)
        if player_name != None:
            # update player action
            for line in self.forward_lines:
                if line.LW != None:
                    if line.LW.name == player_name:
                        line.LW.addPass(action)
                if line.C != None:
                    if line.C.name == player_name:
                        line.C.addPass(action)
                if line.RW != None:
                    if line.RW.name == player_name:
                        line.RW.addPass(action)
            for line in self.defense_lines:
                if line.LD != None:
                    if line.LD.name == player_name:
                        line.LD.addPass(action)
                if line.RD != None:
                    if line.RD.name == player_name:
                        line.RD.addPass(action)
        return
    
    def addShot(self, action, player_name=None, against=False):
        if not against:
            # update team action
            self.shots.append(action)
        if player_name != None:
            # update player action
            for line in self.forward_lines:
                if line.LW != None:
                    if line.LW.name == player_name:
                        line.LW.addShot(action)
                if line.C != None:
                    if line.C.name == player_name:
                        line.C.addShot(action)
                if line.RW != None:
                    if line.RW.name == player_name:
                        line.RW.addShot(action)
            for line in self.defense_lines:
                if line.LD != None:
                    if line.LD.name == player_name:
                        line.LD.addShot(action)
                if line.RD != None:
                    if line.RD.name == player_name:
                        line.RD.addShot(action)
            for goalie in self.goalies:
                if goalie != None:
                    if goalie.name == player_name:
                        goalie.addShot(action)
        return

    def addGoal(self, action, player_name=None, against=False):
        if not against:
            # update team action
            self.goals.append(action)
        if player_name != None:
            # update player action
            for line in self.forward_lines:
                if line.LW != None:
                    if line.LW.name == player_name:
                        line.LW.addGoal(action)
                if line.C != None:
                    if line.C.name == player_name:
                        line.C.addGoal(action)
                if line.RW != None:
                    if line.RW.name == player_name:
                        line.RW.addGoal(action)
            for line in self.defense_lines:
                if line.LD != None:
                    if line.LD.name == player_name:
                        line.LD.addGoal(action)
                if line.RD != None:
                    if line.RD.name == player_name:
                        line.RD.addGoal(action)
            for goalie in self.goalies:
                if goalie != None:
                    if goalie.name == player_name:
                        goalie.addGoal(action)
        return
    
    def addAssist(self, action, player_name=None):
        # update team action
        self.assists.append(action)
        if player_name != None:
            # update player action
            for line in self.forward_lines:
                if line.LW != None:
                    if line.LW.name == player_name:
                        line.LW.addAssist(action)
                if line.C != None:
                    if line.C.name == player_name:
                        line.C.addAssist(action)
                if line.RW != None:
                    if line.RW.name == player_name:
                        line.RW.addAssist(action)
            for line in self.defense_lines:
                if line.LD != None:
                    if line.LD.name == player_name:
                        line.LD.addAssist(action)
                if line.RD != None:
                    if line.RD.name == player_name:
                        line.RD.addAssist(action)
        return
    
    def addFaceoff(self, action, player_name=None):
        # update team action
        self.faceoffs.append(action)
        if player_name != None:
            # update player action
            for line in self.forward_lines:
                if line.LW != None:
                    if line.LW.name == player_name:
                        line.LW.addFaceoff(action)
                if line.C != None:
                    if line.C.name == player_name:
                        line.C.addFaceoff(action)
                if line.RW != None:
                    if line.RW.name == player_name:
                        line.RW.addFaceoff(action)
            for line in self.defense_lines:
                if line.LD != None:
                    if line.LD.name == player_name:
                        line.LD.addFaceoff(action)
                if line.RD != None:
                    if line.RD.name == player_name:
                        line.RD.addFaceoff(action)

    def addShift(self, player_name):
        # update player action
        for line in self.forward_lines:
            if line.LW != None:
                if line.LW.name == player_name:
                    line.LW.addShift()
            elif line.C != None:
                if line.C.name == player_name:
                    line.C.addShift()
            elif line.RW != None:
                if line.RW.name == player_name:
                    line.RW.addShift()
        for line in self.defense_lines:
            if line.LD != None:
                if line.LD.name == player_name:
                    line.LD.addShift()
            elif line.RD != None:
                if line.RD.name == player_name:
                    line.RD.addShift()
        return

    def getFaceoffData(self):
        total_data = []                                     # [name, [#wins, #faceoffs]]
        zone_data = [[], [], [], [], [], [], [], [], []]    # [name, [#wins, #faceoffs]]
        num_zones = 9
        # forwards
        for line in self.forward_lines:
            if line.LW != None:
                if line.LW.faceoffs != []:
                    player = line.LW
                    temp_total_data, temp_zone_data = player.getFaceoffs()
                    total_data.append([player.name, temp_total_data])
                    for zone in range(num_zones):
                        zone_data[zone].append([player.name, temp_zone_data[zone]])
            if line.C != None:
                if line.C.faceoffs != []:
                    player = line.C
                    temp_total_data, temp_zone_data = player.getFaceoffs()
                    total_data.append([player.name, temp_total_data])
                    for zone in range(num_zones):
                        zone_data[zone].append([player.name, temp_zone_data[zone]])
            if line.RW != None:
                if line.RW.faceoffs != []:
                    player = line.RW
                    temp_total_data, temp_zone_data = player.getFaceoffs()
                    total_data.append([player.name, temp_total_data])
                    for zone in range(num_zones):
                        zone_data[zone].append([player.name, temp_zone_data[zone]])
        # defense
        for line in self.defense_lines:
            if line.LD != None:
                if line.LD.faceoffs != []:
                    player = line.LD
                    temp_total_data, temp_zone_data = player.getFaceoffs()
                    total_data.append([player.name, temp_total_data])
                    for zone in range(num_zones):
                        zone_data[zone].append([player.name, temp_zone_data[zone]])
            if line.RD != None:
                if line.RD.faceoffs != []:
                    player = line.RD
                    temp_total_data, temp_zone_data = player.getFaceoffs()
                    total_data.append([player.name, temp_total_data])
                    for zone in range(num_zones):
                        zone_data[zone].append([player.name, temp_zone_data[zone]])
        
        # Bubble sort each zone
        for zone in range(len(zone_data)):
            temp_item = None
            change = True
            while change:
                change = False
                for i in range(len(zone_data[zone])-1):
                    if zone_data[zone][i][1][1] == 0:
                        data1 = 0
                    else:
                        data1 = zone_data[zone][i][1][0]/zone_data[zone][i][1][1]
                    if zone_data[zone][i+1][1][1] == 0:
                        data2 = 0
                    else:
                        data2 = zone_data[zone][i+1][1][0]/zone_data[zone][i+1][1][1]
                    if data1 < data2:
                        change = True
                        temp_item = zone_data[zone][i]
                        zone_data[zone][i] = zone_data[zone][i+1]
                        zone_data[zone][i+1] = temp_item
        
        # Bubble sort total data
        temp_item = None
        change = True
        while change:
            change = False
            for i in range(len(total_data)-1):
                if total_data[i][1][1] == 0:
                    data1 = 0
                else:
                    data1 = total_data[i][1][0]/total_data[i][1][1]
                if total_data[i+1][1][1] == 0:
                    data2 = 0
                else:
                    data2 = total_data[i+1][1][0]/total_data[i+1][1][1]
                if data1 < data2:
                    change = True
                    temp_item = total_data[i]
                    total_data[i] = total_data[i+1]
                    total_data[i+1] = temp_item
    
        return total_data, zone_data

    # zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
    def displayFaceoffData(self):
        total_data, zone_data = self.getFaceoffData()

        img_dir = path.join(path.dirname(__file__), 'img')
        #image = PImage.open(path.join(img_dir, "hockey-rink-diagram_blacknwhite.png"))
        image = PImage.open(path.join(img_dir, "hockey-rink-diagram.png"))
        
        box_size = (20, 70)
        # zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
        box_cords = [(170, 210), (170, 515), (425, 210), (695, 210), (550, 360), (425, 515), (695, 510), (940, 215), (940, 515)]
        
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial", 14, encoding='unic')
        for zone in range(len(zone_data)):
            y_text = 0
            for line in zone_data[zone]:
                if line[1][1] == 0:
                    percent = 0
                else:
                    percent = round((line[1][0]/line[1][1])*100, 2)
                line_text = line[0] + ": " + str(percent) + "% (" + str(line[1][0]) + "/" + str(line[1][1]) +  ")"
                width, height = font.getsize(line_text)
                draw.text((box_cords[zone][0], box_cords[zone][1] + y_text), line_text, font=font, fill=(0, 0, 0))
                y_text += height

        return image

    def getOnNetShots(self):
        temp = []
        for shot in self.shots:
            if shot.on_net:
                temp.append(shot)
        return temp
        

                    


    



class Player():
    def __init__(self, number, name, position):
        self.number = number
        self.name = name
        self.position = position
        self.shots = []
        self.passes = []
        self.goals = []
        self.assists = []
        self.faceoffs = []
        self.shifts = 0

    def addPass(self, action):
        self.passes.append(action)
        return
    
    def addShot(self, action):
        self.shots.append(action)
        return

    def addGoal(self, action):
        self.goals.append(action)
        return

    def addAssist(self, action):
        self.assists.append(action)
        return
    
    def addFaceoff(self, action):
        self.faceoffs.append(action)
        return
    
    def addShift(self):
        self.shifts = self.shifts + 1


    # returns total faceoff numbers and zone faceoff numbers for the player
    def getFaceoffs(self):
        num_zones = 9
        zone_data = []
        total_count = 0
        total_win_count = 0
        for zone in range(num_zones):
            count = 0
            win_count = 0
            for faceoff in self.faceoffs:
                if faceoff.zone == zone:
                    count = count + 1
                    if faceoff.win == True:
                        win_count = win_count + 1
            zone_data.append([win_count, count])
            total_count = total_count + count
            total_win_count = total_win_count + win_count
        total_data = [total_win_count, total_count]
        return total_data, zone_data



class Goalie():
    def __init__(self, number, name, position):
        self.number = number
        self.name = name
        self.position = position
        self.shots_against = []
        self.goals_against = []

    def addShot(self, action):
            self.shots_against.append(action)
            return
    def addGoal(self, action):
            self.goals_against.append(action)
            return


class ForwardLine():
    def __init__(self, LW, C, RW):
        self.LW = LW
        self.C = C
        self.RW = RW
class DefenseLine():
    def __init__(self, LD, RD):
        self.LD = LD
        self.RD = RD




class Pass():
    def __init__(self, start_pos, end_pos, complete, period, ES, PP, PK, high_danger, zone):
        self.start_x = start_pos[0]
        self.start_y = start_pos[1]
        self.end_x = end_pos[0]
        self.end_y = end_pos[1]
        self.complete = complete
        self.period = period
        self.even_strength = ES
        self.PP = PP
        self.PK = PK
        self.high_danger = high_danger
        self.zone = zone    # zones = [D-Zone, Neutral-Zone, O-Zone]

class Shot():
    def __init__(self, pos, on_net, period, ES, PP, PK, high_danger):
        self.x = pos[0]
        self.y = pos[1]
        self.on_net = on_net
        self.period = period
        self.even_strength = ES
        self.PP = PP
        self.PK = PK
        self.high_danger = high_danger

class Goal():
    def __init__(self, pos, period, ES, PP, PK, names_on_the_ice):
        self.x = pos[0]
        self.y = pos[1]
        self.period = period
        self.even_strength = ES
        self.PP = PP
        self.PK = PK
        self.names_on_the_ice = names_on_the_ice    # [X, X, X, X, X]

class Assist():
    def __init__(self, start_pos, end_pos, type, period, ES, PP, PK):
        self.start_x = start_pos[0]
        self.start_y = start_pos[1]
        self.end_x = end_pos[0]
        self.end_y = end_pos[1]
        self.type = type    # 1st assist or 2nd assist
        self.period = period
        self.even_strength = ES
        self.PP = PP
        self.PK = PK

class Faceoff():
    def __init__(self, zone, win, period):
        self.zone = zone    # zones = [d_zone_top, d_zone_bottom, n_zone_top_left, n_zone_top_right, n_zone_center, n_zone_bottom_left, n_zone_bottom_right, o_zone_top, o_zone_bottom]
        self.win = win
        self.period = period




def save_object(obj, filename):
    try:
        with open(filename, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def load_object(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)

    

# TESTING
if __name__ == "__main__":
    import random
    # directories
    player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
    #player_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
    game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
    #game_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
    
    f_line_shifts = [[], [], [], [], []]
    d_line_shifts = [[], [], []]

    file_list = os.listdir(game_path)
    count = 0
    for file in file_list:
        obj = load_object(game_path + file)
        
        #save_object(obj, game_path + file)

    
            
    pass

    print("========== Finished Updates ==========")
    # obj = MyClass(10)
    # save_object(obj, filename)

    # obj = load_object(filename)