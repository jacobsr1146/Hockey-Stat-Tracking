# Main Program

import sys
import pygame
import os
import math
import subprocess
from os import path
import tkinter as tk
from trackStats import *
from getStats import *
from trackDataObjects import *
from tkinter import filedialog as fd

player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
#player_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
#game_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
roster_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/rosters/'
#roster_path = r'C:/Users/jacob/OneDrive/SavedDocuments/HockeyAnalytics/CU_D2_Hockey_23-24/rosters/'

def oldRoster(player_names):
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import askopenfile
    tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

    #fn = askopenfilename()
    filetypes = ( ('text files', '*.txt'), ('All files', '*.*') )
    fn = fd.askopenfile(filetypes=filetypes, initialdir="#Specify the file path")
    file_text = open(fn.name)
    forwards = False
    defense = False
    goalies = False
    for line in file_text:
        if line == "Forwards:\n":
            count = 0
            forwards = True
            defense = False
            goalies = False
        elif line == "Defense:\n":
            count = 0
            forwards = False
            defense = True
            goalies = False
        elif line == "Goalies:\n":
            forwards = False
            defense = False
            goalies = True
        elif line != "":
            if forwards:
                box = forward_option_boxes[count]
                
                # go through LW, C, and RW
                for num in range(3):
                    box[num].selected = 0
                    for i in range(len(player_names)):
                        if player_names[i] == line.split(", ")[num]:
                            box[num].selected = i
                # LW = line.split(", ")[0]
                # C = line.split(", ")[1]
                # RW = line.split(", ")[2]
                # box[0].text = LW
                # box[0].txt_surface = box[0].font.render(box[0].text, True, box[0].color)
                # box[1].text = C
                # box[1].txt_surface = box[1].font.render(box[1].text, True, box[1].color)
                # box[2].text = RW
                # box[2].txt_surface = box[2].font.render(box[2].text, True, box[2].color)
                count = count + 1
            elif defense:
                box = defense_option_boxes[count]

                # go through LD and RD
                for num in range(2):
                    box[num].selected = 0
                    for i in range(len(player_names)):
                        if player_names[i] == line.split(", ")[num]:
                            box[num].selected = i
                # LD = line.split(", ")[0]
                # RD = line.split(", ")[1]
                # box[0].text = LD
                # box[0].txt_surface = box[0].font.render(box[0].text, True, box[0].color)
                # box[1].text = RD
                # box[1].txt_surface = box[1].font.render(box[1].text, True, box[1].color)
                count = count + 1
            elif goalies:
                box = goalie_option_boxes

                # go through starting and backup goalie
                for num in range(2):
                    box[num].selected = 0
                    for i in range(len(player_names)):
                        if player_names[i] == line.split(", ")[num]:
                            box[num].selected = i
                # starter = line.split(", ")[0]
                # backup = line.split(", ")[1]
                # box[0].text = starter
                # box[0].txt_surface = box[0].font.render(box[0].text, True, box[0].color)
                # box[1].text = backup
                # box[1].txt_surface = box[1].font.render(box[1].text, True, box[1].color)

    return


def newRoster(player_names, player_num_pos, forward_box_list, defense_box_list, goalie_box_list, opponent_box, date_box):
    opponent = opponent_box.text
    date = date_box.text
    skater_names = []
    forward_lines = []
    forward_pos = ['LW', 'C', 'RW']
    for line in forward_box_list:
        temp_line = []
        count = -1
        for box in line:
            count = count + 1
            if box.selected != 0:
                num = player_num_pos[box.selected][0]
                name = box.option_list[box.selected]
                temp_line.append(Player(num, name, forward_pos[count]))
                skater_names.append(name)
            else:
                temp_line.append(None)
                skater_names.append("")
        forward_lines.append(ForwardLine(temp_line[0], temp_line[1], temp_line[2]))
    
    defense_lines = []
    defense_pos = ['LD', 'RD']
    for line in defense_box_list:
        temp_line = []
        count = -1
        for box in line:
            count = count + 1
            if box.selected != 0:
                num = player_num_pos[box.selected][0]
                name = box.option_list[box.selected]
                temp_line.append(Player(num, name, defense_pos[count]))
                skater_names.append(name)
            else:
                temp_line.append(None)
                skater_names.append("")
        defense_lines.append(DefenseLine(temp_line[0], temp_line[1]))
    
    goalie_lines = []
    goalie_names = []
    goalie_pos = ['Starter', 'Backup']
    count = -1
    for box in goalie_box_list:
        count = count + 1
        if box.selected != 0:
            num = player_num_pos[box.selected][0]
            name = box.option_list[box.selected]
            goalie_lines.append(Goalie(num, name, goalie_pos[count]))
            goalie_names.append(name)
        else:
            goalie_lines.append(None)
            goalie_names.append("")

    game_object = Game("University of Colorado", opponent, date, forward_lines, defense_lines, goalie_lines)

    trackGameStats(skater_names, goalie_names, game_object)
    return


def oldGame():
    from tkinter.filedialog import askopenfilename
    tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

    fn = askopenfilename()
    game_object = load_object(fn)

    skater_names = []
    goalie_names = []
    for line in game_object.our_team.forward_lines:
        if line.LW != None:
            skater_names.append(line.LW.name)
        else:
            skater_names.append('')
        if line.C != None:
            skater_names.append(line.C.name)
        else:
            skater_names.append('')
        if line.RW != None:
            skater_names.append(line.RW.name)
        else:
            skater_names.append('')

    for line in game_object.our_team.defense_lines:
        if line.LD != None:
            skater_names.append(line.LD.name)
        else:
            skater_names.append('')
        if line.RD != None:
            skater_names.append(line.RD.name)
        else:
            skater_names.append('')
    
    for goalie in game_object.our_team.goalies:
        goalie_names.append(goalie.name)

    trackGameStats(skater_names, goalie_names, game_object)
    return


def save_roster(forward_box_list, defense_box_list, goalie_box_list, opponent_box, date_box):
    # save roster
    filename = "game_roster_" + date_box.text + "_" + opponent_box.text + '.txt'
    roster_file = Path(roster_path + '/' + filename) #add your path lists 
    f = open(roster_file, "x")

    file_text = ""

    file_text = file_text + "Forwards:" + '\n'
    for line in forward_box_list:
        for box in line:
            if box.selected != 0:
                file_text = file_text + box.option_list[box.selected]
            file_text = file_text + ", "
        file_text = file_text + '\n'

    file_text = file_text + "Defense:" + '\n'
    for line in defense_box_list:
        for box in line:
            if box.selected != 0:
                file_text = file_text + box.option_list[box.selected]
            file_text = file_text + ", "
        file_text = file_text + '\n'
    
    file_text = file_text + "Goalies:" + '\n'
    for box in goalie_box_list:
        if box.selected != 0:
            file_text = file_text + box.option_list[box.selected]
        file_text = file_text + ", "
    
    f.write(file_text)
    f.close()

    Tk().wm_withdraw() #to hide the main window
    messagebox.showinfo('Roster Updated', filename + " saved")
    return
    



            
    


def gameRoster():
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

    option_box_width = 290*width_ratio
    option_box_height = 90*height_ratio
    

    num_forward_lines = 5
    num_defense_lines = 4

    temp_box = None
    option_boxes = []
    input_box_list = []
    text_boxes = []

    # Opponent
    opponent_box = InputBox(screen_width - buttonBumper*12, buttonBumper*2, box_width, box_height, font_size32, "Opponent", False)
    input_box_list.append(opponent_box)
    # Date
    date_box = InputBox(screen_width - buttonBumper*12, buttonBumper*3 + box_height, box_width, box_height, font_size32, "Date", False, "YEAR-MO-DY")
    input_box_list.append(date_box)

    global forward_option_boxes
    forward_option_boxes = []

    # create and load player objects from the game objects
    player_names = []
    player_num_pos = []
    player_names.append("None")
    player_num_pos.append((0, "N/A"))
    player_database = open(player_path + 'player database.txt')
    for line in player_database:
        player_num = line.split(", ")[0]
        name = line.split(", ")[1]
        position = line.split(", ")[2][:-1]
        player_names.append(name)
        player_num_pos.append((player_num, position))
    

    # Forwards
    # Text
    text_boxes.append(["Forwards:", (buttonBumper*3, buttonBumper*.5), int(22*width_ratio)])
    positions = ['LW', 'C', 'RW']
    temp_list = []
    j = 0
    i = 0
    for index in range(num_forward_lines*3):
        temp_box = OptionBox(buttonBumper*3  + ((index - i) * (option_box_width + box_bumper*4)), buttonBumper*1.5 + (j * (option_box_height + box_bumper)), option_box_width, option_box_height, player_names, font_size32)
        temp_list.append(temp_box)
        option_boxes.append(temp_box)
        if len(temp_list) == 3:
            forward_option_boxes.append(temp_list)
            temp_list = []
            j = j + 1
            i = i + 3
    
    # Defenseman
    text_boxes.append(["Defense:", (buttonBumper*8, buttonBumper*1.5 + (num_forward_lines * (option_box_height + box_bumper))), int(22*width_ratio)])
    positions = ['LD', 'RD']
    global defense_option_boxes
    defense_option_boxes = []
    temp_list = []
    j = 0
    i = 0
    for index in range(num_defense_lines*2):
        temp_box = OptionBox(buttonBumper*8 + ((index - i) * (option_box_width + box_bumper*4)), buttonBumper*2.5 + (j * (option_box_height + box_bumper)) + (num_forward_lines * (option_box_height + box_bumper)), option_box_width, option_box_height, player_names, font_size32)
        temp_list.append(temp_box)
        option_boxes.append(temp_box)
        if len(temp_list) == 2:
            defense_option_boxes.append(temp_list)
            temp_list = []
            j = j + 1
            i = i + 2

    # Goalies
    text_boxes.append(["Goalies:", ((option_box_width + box_bumper*4)*2 + buttonBumper*12, buttonBumper*3 + (num_forward_lines * (option_box_height + box_bumper))), int(22*width_ratio)])
    positions = ["Starter", "Backup"]
    global goalie_option_boxes
    goalie_option_boxes = []
    for index in range(2):
        temp_box = OptionBox((option_box_width + box_bumper*4)*2 + buttonBumper*12, buttonBumper*4 + (num_forward_lines * (option_box_height + box_bumper)) + (index * (option_box_height + box_bumper)), option_box_width, option_box_height, player_names, font_size32)
        goalie_option_boxes.append(temp_box)
        option_boxes.append(temp_box)


    # Buttons and their respective functions.
    temp_button = None
    buttons = [
        ['Import Old Game', lambda: oldGame()],
        ['Import Old Roster', lambda: oldRoster(player_names)],
        ['Save Current Roster', lambda: save_roster(forward_option_boxes, defense_option_boxes, goalie_option_boxes, opponent_box, date_box)],
        ['Use Current Roster', lambda: newRoster(player_names, player_num_pos, forward_option_boxes, defense_option_boxes, goalie_option_boxes, opponent_box, date_box)]
    ]

    # Making the buttons
    for index, buttonDetails in enumerate(buttons):
        temp_button = NormalButton(screen_width - buttonBumper*12, buttonBumper*6 + (index * (buttonHeight + buttonBumper*2)), buttonWidth, buttonHeight, font_size32, buttonDetails[0], buttonDetails[1])
        objects.append(temp_button)

    # reverse order of option boxes
    temp_option_boxes = []
    for box in option_boxes:
        temp_option_boxes.insert(0, box)
    option_boxes = temp_option_boxes
    
    quit = False

    # Game loop.
    while not quit:
        screen.fill((30, 30, 30))

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                quit = True
                pygame.quit()
                sys.exit()

            for box in input_box_list:
                box.handle_event(event, input_box_list)

        # Drawing the Buttons
        for object in objects:
            object.process()
            screen.blit(object.buttonSurface, object.buttonRect)
        
        # Drawing the Input Boxes
        for box in input_box_list:
            box.rect.w = max(200*width_ratio, (box.txt_surface.get_width()+10))
        for box in input_box_list:
            box.draw(screen)

        # Drawing Text
        for text in text_boxes:
            screen.blit(pygame.font.SysFont('Arial', text[2]).render(text[0], False, (250, 250, 250)), text[1])

        # Drawing Option Boxes
        for box in option_boxes:
            box.draw(screen)
            selected_option = box.update(event_list)
            

        

        pygame.display.flip()
        #fpsClock.tick(fps)
        fpsClock.tick()
