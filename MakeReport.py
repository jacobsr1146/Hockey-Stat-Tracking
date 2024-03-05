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
from tracemalloc import Snapshot
import openpyxl
import pandas as pd
import seaborn as sns
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader

player_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/player_objects/'
game_path = r'C:/Users/Jacob/OneDrive/Documents/HockeyAnalytics/CU_D2_Hockey_23-24/game_objects/'
img_dir = path.join(path.dirname(__file__), 'img') + "\\"

def makeReport(player_obj, stat):

    # Create the watermark from an image
    c = canvas.Canvas(str(date.today()) + " " + player_obj.name + ' Report.pdf')
    canvas_width, canvas_height = c._pagesize

    margin = 20
    header = canvas_height - margin - 80
    num_rows = 3
    row_diff = (header - (margin*2)) / num_rows

    row1 = header - margin - row_diff
    row2 =  row1 - row_diff
    row3 = row2 - row_diff
    column1 = margin + 10
    column2 = canvas_width/2 + 30

    # Logos
    logo_height = canvas_height - header - margin
    logo_width = logo_height + 40


    # SHOOTING STATS
    if stat == "Shooting" or stat == "All":
        # Logos
        c.drawImage(img_dir + 'cu_hockey_logo.png', margin, header, logo_width, logo_height)
        c.drawImage(img_dir + 'BMHC_logo.png', canvas_width - margin - logo_width, header, logo_width + 10, logo_height + 10)

        # Name
        c.setFontSize(30)
        c.drawCentredString(canvas_width/2, header + ((canvas_height - margin - header)/2), player_obj.name)
        
        c.setFontSize(18)
        offset = 100
        if player_obj.position != "G":
            # Skater Stats

            # Title
            c.setFontSize(20)
            c.drawCentredString(canvas_width/2, header + ((canvas_height - margin - header)/2) - 20, "Shooting Stats")

            # Numbers
            c.drawString(column2, header - offset, "Total Goals: " + str(player_obj.goals))
            c.drawString(column2, header - offset - 20, "Total Shots: " + str(player_obj.shots))
            if player_obj.shots != 0:
                c.drawString(column2, header - offset - 40, "Shooting %: " + str(round((player_obj.goals/player_obj.shots)*100, 2)) + "%")
                c.drawString(column2, header - offset - 60, "On Net %: " + str(round((player_obj.shots_on_net/player_obj.shots)*100, 2)) + "%")
                c.drawString(column2, header - offset - 80, "High Danger %: " + str(round((player_obj.shots_high_danger/player_obj.shots)*100, 2)) + "%")
            else:
                c.drawString(column2, header - offset - 40, "Shooting %: N/A")
                c.drawString(column2, header - offset - 60, "On Net Shot %: N/A")
                c.drawString(column2, header - offset - 80, "High Danger Shot %: N/A")

            # Images
            img1 = player_obj.shots_time_graph
            img2 = player_obj.shots_on_net_time_graph
            
            
            # Legend
            c.setFontSize(6)
            c.drawString(margin, 14, "Shooting % - Percentage of shots taken that result in a goal.")
            c.drawString(margin, 8, "On Net % - Percentage of shots taken that are on net.")
            c.drawString(margin, 2, "High Danger % - Percentage of shots taken that are taken below the tops of the circles and between the faceoff dots.")
        else:
            # Goalie Stats

            # Title
            c.setFontSize(20)
            c.drawCentredString(canvas_width/2, header + ((canvas_height - margin - header)/2) - 20, "Goalie Stats")

            # Numbers
            c.drawString(column2, header - offset, "Goals Allowed: " + str(player_obj.goals))
            c.drawString(column2, header - offset - 20, "Shots Saved: " + str(player_obj.shots - player_obj.goals))
            if player_obj.shots != 0:
                c.drawString(column2, header - offset - 40, "GAA: " + str(player_obj.gaa))
                c.drawString(column2, header - offset - 60, "SV %: " + str(round(player_obj.sv_percent, 3)) + "%")
                c.drawString(column2, header - offset - 80, "Saves per Game: " + str(player_obj.sv_per_game))
            else:
                c.drawString(column2, header - offset - 40, "GAA: N/A")
                c.drawString(column2, header - offset - 60, "SV %: N/A")
                c.drawString(column2, header - offset - 80, "Saves per Game: N/A")
            
            # Images
            img1 = player_obj.goals_against_time_graph
            img2 = player_obj.save_percent_time_graph
            
        # Image 1
        if img1 != None:
            img = img1
            pygame.image.save(img, "temp_img2.png")
            new_height = row_diff
            new_width = (img.get_width() * new_height)/img.get_height()
            c.drawImage('temp_img2.png', canvas_width/2 - new_width/2 - 50, row2, new_width + 100, new_height)

        # Image 2
        if img2 != None:
            img = img2
            pygame.image.save(img, "temp_img3.png")
            new_height = row_diff
            new_width = (img.get_width() * new_height)/img.get_height()
            c.drawImage('temp_img3.png', canvas_width/2 - new_width/2 - 50, row3, new_width + 100, new_height)

        # Shot Map
        if player_obj.shots_map != None:
            img = player_obj.shots_map
            pygame.image.save(img, "temp_img1.png")
            new_height = row_diff
            new_width = (img.get_width() * new_height)/img.get_height()
            c.drawImage('temp_img1.png', column1, row1, new_width + 50, new_height)
 
        
        #Close the current page and possibly start on a new page.
        c.showPage()

    # FACEOFF STATS
    do_faceoffs = False
    for zone in player_obj.faceoffs_taken:
        if zone > 0:
            do_faceoffs = True
    if (stat == "Faceoffs" or stat == "All") and do_faceoffs:
        # Logos
        c.drawImage(img_dir + 'cu_hockey_logo.png', margin, header, logo_width, logo_height)
        c.drawImage(img_dir + 'BMHC_logo.png', canvas_width - margin - logo_width, header, logo_width + 10, logo_height + 10)

        # Name
        c.setFontSize(30)
        c.drawCentredString(canvas_width/2, header + ((canvas_height - margin - header)/2), player_obj.name)

        # Title
        c.setFontSize(20)
        c.drawCentredString(canvas_width/2, header + ((canvas_height - margin - header)/2) - 20, "Faceoff Stats")

        # Numbers
        c.setFontSize(18)
        offset = 100
        c.drawString(column2 + 90, header - offset, "Total: " + str(player_obj.faceoff_total_percent) + "%")
        c.drawString(column2 + 90, header - offset - 20, "D-Zone: " + str(player_obj.faceoff_d_percent) + "%")
        c.drawString(column2 + 90, header - offset - 40, "Neutral-Zone: " + str(player_obj.faceoff_n_percent) + "%")
        c.drawString(column2 + 90, header - offset - 60, "O-Zone: " + str(player_obj.faceoff_o_percent) + "%")
        c.drawString(column2 + 90, header - offset - 80, "Left Side: " + str(player_obj.faceoff_left_percent) + "%")
        c.drawString(column2 + 90, header - offset - 100, "Right Side: " + str(player_obj.faceoff_right_percent) + "%")

        # Load input image
        if player_obj.faceoff_map != None:
            img = player_obj.faceoff_map
            pygame.image.save(img, "temp_img4.png")
            new_height = row_diff
            new_width = (img.get_width() * new_height)/img.get_height()
            c.drawImage('temp_img4.png', column1, row1, new_width, new_height)
 
        if player_obj.faceoff_time_graph != None:
            img = player_obj.faceoff_time_graph
            pygame.image.save(img, "temp_img5.png")
            new_height = row_diff
            new_width = (img.get_width() * new_height)/img.get_height()
            c.drawImage('temp_img5.png', canvas_width/2 - new_width/2 - 50, row2, new_width + 100, new_height)

        if player_obj.faceoff_detailed_time_graph != None:
            img = player_obj.faceoff_detailed_time_graph
            pygame.image.save(img, "temp_img6.png")
            new_height = row_diff
            new_width = (img.get_width() * new_height)/img.get_height()
            c.drawImage('temp_img6.png', canvas_width/2 - new_width/2 - 50, row3, new_width + 100, new_height)

        #Close the current page and possibly start on a new page.
        c.showPage()
      
    c.save()
    
    print(player_obj.name + "'s report created successfully")

    return


if __name__ == "__main__":

    pass
    

