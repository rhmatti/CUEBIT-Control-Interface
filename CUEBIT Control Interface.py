#CUEBIT Control Interface
#Author: Richard Mattish
#Last Updated: 02/25/2023


#Function:  This program provides a graphical user interface for controlling
#           and monitoring the Clemson University EBIT.


#Import General Tools
import sys
import os
import platform
import time
from turtle import bgcolor
import webbrowser
import threading

#Import GUI Tools
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image

#Import Server Tools
from data_client import BaseDataClient

#Import Math Tools
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import scipy as sp
import pandas as pd


# Set true for if running dummy server.
#DEBUG = False
DEBUG = True

import data_client
ADDR = data_client.ADDR
try:
    import socket
    on_network = str(socket.gethostbyname(socket.gethostname())).startswith('192.168.0.')
    if not on_network:
        DEBUG = True
except:
    pass

if DEBUG:
    ADDR = ("130.127.188.254", 20002)


#Defines location of the Desktop as well as font and text size for use in the software
desktop = os.path.expanduser("~\Desktop")
desktop = desktop.replace(os.sep, '/')
font_12 = ('Helvetica', 12)
font_14 = ('Helvetica', 14)
font_16 = ('Helvetica', 16)
font_18 = ('Helvetica', 18)
font_20 = ('Helvetica', 20)

#Opens a url in a new tab in the default webbrowser
def callback(url):
    webbrowser.open_new_tab(url)

#Sorts all columns of a matrix by a single column
def orderMatrix(matrix, column):
    i = 0
    a = len(matrix)
    orderedMatrix = []
    while i < len(matrix):
        j = 0
        smallest = True
        while j < len(matrix) and smallest == True:
            if matrix[i][column] <= matrix[j][column]:
                smallest = True
                j = j + 1
            else:
                smallest = False
        if smallest == True:
            orderedMatrix.append(matrix.pop(i))
            i = 0
        else:
            i = i + 1
    return orderedMatrix

#Enables multi-threading so that function will not freeze main GUI
def multiThreading(function):
    t1=threading.Thread(target=function)
    t1.setDaemon(True)      #This is so the thread will terminate when the main program is terminated
    t1.start()

#Initializes the program
def startProgram(root=None):
    instance = EBIT()
    instance.makeGui(root)

#This is the EBIT class object, which contains everything related to the GUI control interface
class EBIT:
    def __init__(self):
        #Establishes connection to Server
        try:
            self.client = BaseDataClient(ADDR)
            self.client.select()
        except:
            print('Error: Could not establish connection to server')


        #Defines global variables
        self.canvas = None
        self.fig = None
        self.ax = None
        self.toolbar = None
        self.filename = None
        self.work_dir = None

        #Arrays for plots
        self.time_array = []
        self.anode_array = []

        #Cathode Variables
        self.U_cat = None
        self.I_heat = None
        self.I_heat_set = None
        self.I_cat = None
        self.U_filament = None
        self.U_cat_set = None

        #Anode Variables
        self.U_an = None
        self.I_an = None
        self.U_an_set = None

        #Drift Tube Variables
        self.U_0 = None
        self.U_0_set = None
        self.I_dt = None
        self.U_A = None
        self.U_A_set= None
        self.U_B1 = None
        self.U_B2 = None
        self.U_B = None
        self.dt_timer = False
        self.t_ion = None
        self.t_ion_set = None
        self.t_ext = None
        self.t_ext_set = None

        #Faraday Cup Variables
        self.FC1 = None
        self.FC2 = None
        self.FC1_I = None
        self.FC2_I = None

        #Lens Variables
        self.U_ext = None
        self.U_ext_set = None
        self.U_EL1 = None
        self.U_EL1_set = None
        self.U_EL2 = None
        self.U_EL2_set = None

        #Deflector Variables
        self.U_X1_A = None
        self.U_X1_B = None
        self.U_X1_set = None
        self.U_Y1_A = None
        self.U_Y1_B = None
        self.U_Y1_set = None
        self.U_X2_A = None
        self.U_X2_B = None
        self.U_X2_set = None
        self.U_Y2_A = None
        self.U_Y2_B = None
        self.U_Y2_set = None

        #Gas Valve Variables
        self.P_Valve = None

        #Deceleration Variables
        self.U_DL1 = None
        self.U_DL2 = None
        self.U_DL3 = None

        #Status Interlocks
        self.water = None
        self.air = None
        self.power_FUG = None
        self.press_GND = None
        self.press_HV = None
        self.HV_beamline_relay = None
        self.HV_cabinet = None
        self.GND_cabinet = None
        self.doors = None
        self.EMO = None

        #Power Buttons
        self.U_cat_power = False
        self.I_heat_power = False
        self.anode_power = False
        self.dt_power = False
        self.U_ext_power = False
        self.U_EL1_power = False
        self.U_EL2_power = False
        self.U_X1_power = False
        self.U_Y1_power = False
        self.U_X2_power = False
        self.U_Y2_power = False

        #Other Buttons
        self.U_EL1_q = 1
        self.U_EL2_q = 1

        try:
            #Read Cathode variable values from server
            self.U_cat = self.client.get_float('Cathode_Voltage_Read')[1]
            self.I_cat = self.client.get_float('Cathode_Emission')[1]
            self.I_heat = self.client.get_float('Cathode_Heater_Current_Read')[1]

            #Read Anode variable values from server
            self.U_an = self.client.get_float('Anode_Voltage_Read')[1]
            self.I_an = self.client.get_float('Anode_Current')[1]

            #Read Drfit Tube variable values from server
            self.t_ion = self.client.get_float('Drift_Tubes_T_Ion')[1]
            self.t_ext = self.client.get_float('Drift_Tubes_T_Ext')[1]
            self.U_0 = self.client.get_float('Drift_Tubes_U0_Read')[1]
            self.U_A = self.client.get_float('Drift_Tubes_UA_Read')[1]
            self.U_B = self.client.get_float('Drift_Tubes_UB')[1]
            self.I_dt = self.client.get_float('Drift_Tubes_Current')[1]

            #Read Lens variable values from server
            self.U_ext = self.client.get_float('Extraction_Voltage_Read')[1]
            self.U_EL1 = self.client.get_float('Lens_1_Voltage_Read')[1]
            self.U_EL2 = self.client.get_float('Lens_2_Voltage_Read')[1]

            #Read Deflector variable values from server
            self.U_X1_A = self.client.get_float('Deflectors_XY1_XA')[1]
            self.U_X1_B = self.client.get_float('Deflectors_XY1_XB')[1]
            self.U_Y1_A = self.client.get_float('Deflectors_XY1_YA')[1]
            self.U_Y1_B = self.client.get_float('Deflectors_XY1_YB')[1]
            self.U_X2_A = self.client.get_float('Deflectors_XY2_XA')[1]
            self.U_X2_B = self.client.get_float('Deflectors_XY2_XB')[1]
            self.U_Y2_A = self.client.get_float('Deflectors_XY2_YA')[1]
            self.U_Y2_B = self.client.get_float('Deflectors_XY2_YB')[1]

        except:
            #Read Cathode variable values from server
            self.U_cat = 0
            self.I_cat = 0.00

            #Read Anode variable values from server
            self.U_an = 0
            self.I_an = 0

            #Read Drfit Tube variable values from server
            self.t_ion = 3000
            self.t_ext = 3000
            self.U_0 = 0
            self.U_A = 0
            self.U_B = 0

            #Read Lens variable values from server
            self.U_ext = 0
            self.U_EL1 = 0
            self.U_EL2 = 0

            #Read Deflector variable values from server
            self.U_X1_A = 0
            self.U_X1_B = 0
            self.U_Y1_A = 0
            self.U_Y1_B = 0
            self.U_X2_A = 0
            self.U_X2_B = 0
            self.U_Y2_A = 0
            self.U_Y2_B = 0

        #Currently initializes variables just for testing purposes. Later, we will read in the actual values in the try block above
        if True:
            #Defines global variables
            self.canvas = None
            self.fig = None
            self.ax = None
            self.toolbar = None
            self.filename = None
            self.work_dir = None
            
            #Arrays for plots
            self.time_array = []
            self.anode_array = []

            #Cathode Variables
            self.I_heat_set = 0
            self.U_filament = 0.00
            self.U_cat_set = 0

            #Anode Variables
            self.U_an_set = 0

            #Drift Tube Variables
            self.t_ion_set = 3000
            self.t_ext_set = 3000
            self.U_0_set = 4500
            self.U_A_set = 500
            self.U_B1 = 0
            self.U_B2 = 456

            #Faraday Cup Variables
            self.FC1 = 0
            self.FC2 = 0
            self.FC1_I = 0
            self.FC2_I = 0

            #Lens Variables
            self.U_ext_set = 0
            self.U_EL1_set = 0
            self.U_EL2_set = 0

            #Deflector Variables
            self.U_X1_set = 0
            self.U_Y1_set = 0
            self.U_X2_set = 0
            self.U_Y2_set = 0

            #Gas Valve Variables
            self.Gas_Valve = 0

            #Deceleration Variables
            self.U_DL1 = 0
            self.U_DL2 = 0
            self.U_DL3 = 0

            #Status Interlocks
            self.water = False
            self.air = True
            self.power_FUG = True
            self.press_GND = True
            self.press_HV = True
            self.HV_beamline_relay = False
            self.HV_cabinet = True
            self.GND_cabinet = False
            self.doors = True
            self.EMO = False

    def quitProgram(self):
        print('quit')
        self.root.quit()
        self.root.destroy()
    
    #Opens About Window with description of software
    def About(self):
        name = "CUEBIT Control Center"
        version = 'Version: 1.0.0'
        date = 'Date: 02/25/2023'
        support = 'Support: '
        url = 'https://github.com/rhmatti/CUEBIT-Control-Interface'
        copyrightMessage ='Copyright © 2023 Richard Mattish All Rights Reserved.'
        t = Toplevel(self.root)
        t.wm_title("About")
        t.geometry("400x300")
        t.resizable(False, False)
        t.configure(background='white')
        if platform.system() == 'Windows':
            try:
                t.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        l1 = Label(t, text = name, bg='white', fg='blue', font=font_14)
        l1.place(relx = 0.15, rely = 0.14, anchor = W)
        l2 = Label(t, text = version, bg='white', font=font_12)
        l2.place(relx = 0.15, rely = 0.25, anchor = W)
        l3 = Label(t, text = date, bg='white', font=font_12)
        l3.place(relx = 0.15, rely = 0.35, anchor = W)
        l4 = Label(t, text = support, bg = 'white', font=font_12)
        l4.place(relx = 0.15, rely = 0.45, anchor = W)
        l5 = Label(t, text = 'https://github.com/rhmatti/\nCUEBIT-Control-Interface', bg = 'white', fg = 'blue', font=font_12)
        l5.place(relx = 0.31, rely=0.48, anchor = W)
        l5.bind("<Button-1>", lambda e:
        callback(url))
        messageVar = Message(t, text = copyrightMessage, bg='white', font = font_12, width = 600)
        messageVar.place(relx = 0.5, rely = 1, anchor = S)
    
    def Instructions(self):
        instructions = Toplevel(self.root)
        instructions.geometry('1280x720')
        instructions.wm_title("User Instructions")
        instructions.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                instructions.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        v = Scrollbar(instructions, orient = 'vertical')
        t = Text(instructions, font = font_12, bg='white', width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
        t.insert(END, "*********************************************************************************************************************\n")
        t.insert(END, "Program: CUEBIT Control Center\n")
        t.insert(END, "Author: Richard Mattish\n")
        t.insert(END, "Last Updated: 02/24/2022\n\n")
        t.insert(END, "Function:  This program provides a graphical user interface for controlling\n")
        t.insert(END, "\tand monitoring the Clemson University EBIT\n")
        t.insert(END, "*********************************************************************************************************************\n\n\n\n")
        t.insert(END, "User Instructions\n-------------------------\n")
        t.insert(END, "Add Instructions Here Later")

        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)

    def click_button(self, button, type, variable, text=None):
        if type == 'power':
            self.update_button_var(variable, True)
            button.config(bg='#50E24B', command=lambda: self.declick_button(button, type, variable), activebackground='#50E24B')

        elif type == 'timer':
            button.config(bg='#50E24B', text='Timer ON', command=lambda: self.declick_button(button, type, variable), activebackground='#50E24B')
            self.dt_timer = True

        elif type == 'charge':
            self.update_button_var(variable, -1)
            if text != None:
                button.config(bg='#50E24B', text='negative', command=lambda: self.declick_button(button, type, variable, text), activebackground='#50E24B')
                text.config(text = '= -')
            else:
                button.config(bg='#50E24B', text='negative', command=lambda: self.declick_button(button, type, variable), activebackground='#50E24B')


    def declick_button(self, button, type, variable, text=None):
        if type == 'power':
            self.update_button_var(variable, False)
            button.config(bg='grey90', command=lambda: self.click_button(button, type, variable), activebackground='grey90')

        elif type == 'timer':
            button.config(bg='#1AA5F6', text='Timer OFF', command=lambda: self.click_button(button, type, variable), activebackground='#1AA5F6')
            self.dt_timer = False

        elif type == 'charge':
            self.update_button_var(variable, 1)
            if text != None:
                button.config(bg='#1AA5F6', text='positive', command=lambda: self.click_button(button, type, variable, text), activebackground='#1AA5F6')
                text.config(text = '=  ')
            else:
                button.config(bg='#1AA5F6', text='positive', command=lambda: self.click_button(button, type, variable), activebackground='#1AA5F6')

    def update_button_var(self, variable, value):
        if variable == 'U_cat':
            self.client.set_bool('Cathode_Voltage_Power', value)
            print('Cathode voltage power button pressed')
        elif variable == 'I_heat':
            self.client.set_bool('Cathode_Heater_Power', value)
            print('Cathode heater power button pressed')
        elif variable == 'dt_power':
            self.client.set_bool('Drift_Tubes_Power', value)
            print('Drift tubes power button pressed')
        elif variable == 'anode_power':
            self.client.set_bool('Anode_Voltage_Power', value)
            print('Anode power button pressed')
        elif variable == 'U_ext':
            self.client.set_bool('Extraction_Voltage_Power', value)
            print('Extraction voltage power button pressed')
        elif variable == 'U_EL1':
            self.client.set_bool('Lens_1_Voltage_Power', value)
            print('Lens 1 voltage power button pressed')
        elif variable == 'U_EL1_charge':
            self.client.set_int('Lens_1_Polarity', value)
            print('Lens 1 polarity button pressed')
        elif variable == 'U_EL2_charge':
            self.client.set_int('Lens_2_Polarity', value)
            print('Lens 2 polarity button pressed')
        elif variable == 'U_EL2':
            self.client.set_bool('Lens_2_Voltage_Power', value)
            print('Lens 2 voltage power button pressed')
        elif variable == 'U_X1':
            self.client.set_bool('Deflectors_XY1_X_Power', value)
            print('Deflector X1 voltage power button pressed')
        elif variable == 'U_Y1':
            self.client.set_bool('Deflectors_XY1_Y_Power', value)
            print('Deflector Y1 voltage power button pressed')
        elif variable == 'U_X2':
            self.client.set_bool('Deflectors_XY2_X_Power', value)
            print('Deflector X2 voltage power button pressed')
        elif variable == 'U_Y2':
            self.client.set_bool('Deflectors_XY2_Y_Power', value)
            print('Deflector Y2 voltage power button pressed')

    def animate(self, i):
        self.anode_ax.clear()
        xdata = self.time_array
        ydata = self.anode_array
        self.anode_ax.plot(xdata,ydata)
        #self.anode_ax.set_ylabel('Potential (V)')
        self.anode_ax.set_ylim(0,12000)


    #This function runs is run in a separate thread and runs continuously
    #It reads values of all PLC variables and updates them in the display
    def data_reader(self):
        t0 = time.time()
        while True:
            #Read Cathode variable values from server
            U_cat_power = self.client.get_bool('Cathode_Voltage_Power')[1]
            if self.U_cat_power != U_cat_power:
                self.U_cat_power = U_cat_power
                if self.U_cat_power:
                    self.U_cat_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_cat_button, 'power', 'U_cat'), activebackground='#50E24B')
                else:
                    self.U_cat_button.config(bg='grey90', command=lambda: self.click_button(self.U_cat_button, 'power', 'U_cat'), activebackground='grey90')
                
            self.U_cat = self.client.get_float('Cathode_Voltage_Read')[1]
            self.U_cat_actual.config(text=f'{int(round(-1*self.U_cat,0))} V')

            I_heat_power = self.client.get_bool('Cathode_Heater_Power')[1]
            if self.I_heat_power != I_heat_power:
                self.I_heat_power = I_heat_power
                if self.I_heat_power:
                    self.I_heat_button.config(bg='#50E24B', command=lambda: self.declick_button(self.I_heat_button, 'power', 'I_heat'), activebackground='#50E24B')
                else:
                    self.I_heat_button.config(bg='grey90', command=lambda: self.click_button(self.I_heat_button, 'power', 'I_heat'), activebackground='grey90')
                
            self.I_cat = self.client.get_float('Cathode_Emission')[1]
            self.I_cat_label.config(text=f'{round(self.I_cat,1)} mA')

            self.I_heat = self.client.get_float('Cathode_Heater_Current_Read')[1]
            self.I_heat_actual.config(text=f'{round(self.I_heat,2)} A')


            #Read Anode variable values from server
            anode_power = self.client.get_bool('Anode_Voltage_Power')[1]
            if self.anode_power != anode_power:
                self.anode_power = anode_power
                if self.anode_power:
                    self.anode_button.config(bg='#50E24B', command=lambda: self.declick_button(self.anode_button, 'power', 'anode_power'), activebackground='#50E24B')
                else:
                    self.anode_button.config(bg='grey90', command=lambda: self.click_button(self.anode_button, 'power', 'anode_power'), activebackground='grey90')
                
            self.U_an = self.client.get_float('Anode_Voltage_Read')[1]
            self.U_an_actual_label4.config(text = f'{int(round(self.U_an,0))}')

            self.I_an = self.client.get_float('Anode_Current')[1]
            self.I_an_label4.config(text=f'{round(self.I_an,0)}')

            if len(self.anode_array) > 10:
                self.anode_array.pop(0)
                self.time_array.pop(0)
            self.anode_array.append(self.U_an)
            self.time_array.append(time.time()-t0)


            #Read Drfit Tube variable values from server
            dt_power = self.client.get_bool('Drift_Tubes_Power')[1]
            if self.dt_power != dt_power:
                self.dt_power = dt_power
                if self.dt_power:
                    self.dt_button.config(bg='#50E24B', command=lambda: self.declick_button(self.dt_button, 'power', 'dt_power'), activebackground='#50E24B')
                else:
                    self.dt_button.config(bg='grey90', command=lambda: self.click_button(self.dt_button, 'power', 'dt_power'), activebackground='grey90')
                
            self.t_ion = self.client.get_float('Drift_Tubes_T_Ion')[1]
            self.t_ext = self.client.get_float('Drift_Tubes_T_Ext')[1]

            self.U_0 = self.client.get_float('Drift_Tubes_U0_Read')[1]
            self.U_0_actual.config(text=f'{int(round(self.U_0,0))} V')

            self.U_A = self.client.get_float('Drift_Tubes_UA_Read')[1]
            self.U_A_actual.config(text="-{:.1f} V".format(self.U_A))

            self.U_B = self.client.get_float('Drift_Tubes_UB')[1]
            self.U_B_actual.config(text="-{:.1f} V".format(self.U_B))

            self.I_dt = self.client.get_float('Drift_Tubes_Current')[1]
            self.I_dt_label.config(text=f'{int(round(self.I_dt,0))} μA')
            

            #Read Lens variable values from server
            U_ext_power = self.client.get_bool('Extraction_Voltage_Power')[1]
            if self.U_ext_power != U_ext_power:
                self.U_ext_power = U_ext_power
                if self.U_ext_power:
                    self.U_ext_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_ext_button, 'power', 'U_ext'), activebackground='#50E24B')
                else:
                    self.U_ext_button.config(bg='grey90', command=lambda: self.click_button(self.U_ext_button, 'power', 'U_ext'), activebackground='grey90')
                
            self.U_ext = self.client.get_float('Extraction_Voltage_Read')[1]
            if self.U_ext > 0:
                self.U_ext_actual.config(text=f'-{int(round(self.U_ext,0))} V')
            elif self.U_ext == 0:
                self.U_ext_actual.config(text=f'{int(round(self.U_ext,0))} V')

            U_EL1_power = self.client.get_bool('Lens_1_Voltage_Power')[1]
            if self.U_EL1_power != U_EL1_power:
                self.U_EL1_power = U_EL1_power
                if self.U_EL1_power:
                    self.U_EL1_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_EL1_button, 'power', 'U_EL1'), activebackground='#50E24B')
                else:
                    self.U_EL1_button.config(bg='grey90', command=lambda: self.click_button(self.U_EL1_button, 'power', 'U_EL1'), activebackground='grey90')
            
            U_EL1_q = self.client.get_int('Lens_1_Polarity')[1]
            if self.U_EL1_q != U_EL1_q:
                self.U_EL1_q = U_EL1_q
                if self.U_EL1_q == -1:
                    self.U_EL1_charge.config(bg='#50E24B', command=lambda: self.declick_button(self.U_EL1_charge, 'charge', 'U_EL1_charge', self.U_EL1_label3), activebackground='#50E24B')
                else:
                    self.U_EL1_charge.config(bg='#1AA5F6', command=lambda: self.click_button(self.U_EL1_charge, 'charge', 'U_EL1_charge', self.U_EL1_label3), activebackground='#1AA5F6')

            self.U_EL1 = self.client.get_float('Lens_1_Voltage_Read')[1]
            self.U_EL1_actual.config(text=f'{int(round(self.U_EL1_q*self.U_EL1,0))} V')

            U_EL2_power = self.client.get_bool('Lens_2_Voltage_Power')[1]
            if self.U_EL2_power != U_EL2_power:
                self.U_EL2_power = U_EL2_power
                if self.U_EL2_power:
                    self.U_EL2_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_EL2_button, 'power', 'U_EL2'), activebackground='#50E24B')
                else:
                    self.U_EL2_button.config(bg='grey90', command=lambda: self.click_button(self.U_EL2_button, 'power', 'U_EL2'), activebackground='grey90')

            U_EL2_q = self.client.get_int('Lens_2_Polarity')[1]
            if self.U_EL2_q != U_EL2_q:
                self.U_EL2_q = U_EL2_q
                if self.U_EL2_q == -1:
                    self.U_EL2_charge.config(bg='#50E24B', command=lambda: self.declick_button(self.U_EL2_charge, 'charge', 'U_EL2_charge', self.U_EL2_label3), activebackground='#50E24B')
                else:
                    self.U_EL2_charge.config(bg='#1AA5F6', command=lambda: self.click_button(self.U_EL2_charge, 'charge', 'U_EL2_charge', self.U_EL2_label3), activebackground='#1AA5F6')
            
            self.U_EL2 = self.client.get_float('Lens_2_Voltage_Read')[1]
            self.U_EL2_actual.config(text=f'{int(round(self.U_EL2_q*self.U_EL2,0))} V')


            #Read Deflector variable values from server
            U_X1_power = self.client.get_bool('Deflectors_XY1_X_Power')[1]
            if self.U_X1_power != U_X1_power:
                self.U_X1_power = U_X1_power
                if self.U_X1_power:
                    self.U_X1_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_X1_button, 'power', 'U_X1'), activebackground='#50E24B')
                else:
                    self.U_X1_button.config(bg='grey90', command=lambda: self.click_button(self.U_X1_button, 'power', 'U_X1'), activebackground='grey90')

            self.U_X1_A = self.client.get_float('Deflectors_XY1_XA')[1]
            self.U_X1_A_actual.config(text=f'{round(float(self.U_X1_A),1)} V')
            self.U_X1_B = self.client.get_float('Deflectors_XY1_XB')[1]
            self.U_X1_B_actual.config(text=f'{round(float(self.U_X1_B),1)} V')

            U_Y1_power = self.client.get_bool('Deflectors_XY1_Y_Power')[1]
            if self.U_Y1_power != U_Y1_power:
                self.U_Y1_power = U_Y1_power
                if self.U_Y1_power:
                    self.U_Y1_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_Y1_button, 'power', 'U_Y1'), activebackground='#50E24B')
                else:
                    self.U_Y1_button.config(bg='grey90', command=lambda: self.click_button(self.U_Y1_button, 'power', 'U_Y1'), activebackground='grey90')

            self.U_Y1_A = self.client.get_float('Deflectors_XY1_YA')[1]
            self.U_Y1_A_actual.config(text=f'{round(float(self.U_Y1_A),1)} V')
            self.U_Y1_B = self.client.get_float('Deflectors_XY1_YB')[1]
            self.U_Y1_B_actual.config(text=f'{round(float(self.U_Y1_B),1)} V')

            U_X2_power = self.client.get_bool('Deflectors_XY2_X_Power')[1]
            if self.U_X2_power != U_X2_power:
                self.U_X2_power = U_X2_power
                if self.U_X2_power:
                    self.U_X2_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_X2_button, 'power', 'U_X2'), activebackground='#50E24B')
                else:
                    self.U_X2_button.config(bg='grey90', command=lambda: self.click_button(self.U_X2_button, 'power', 'U_X2'), activebackground='grey90')

            self.U_X2_A = self.client.get_float('Deflectors_XY2_XA')[1]
            self.U_X2_A_actual.config(text=f'{round(float(self.U_X2_A),1)} V')
            self.U_X2_B = self.client.get_float('Deflectors_XY2_XB')[1]
            self.U_X2_B_actual.config(text=f'{round(float(self.U_X2_B),1)} V')

            U_Y2_power = self.client.get_bool('Deflectors_XY2_Y_Power')[1]
            if self.U_Y2_power != U_Y2_power:
                self.U_Y2_power = U_Y2_power
                if self.U_Y2_power:
                    self.U_Y2_button.config(bg='#50E24B', command=lambda: self.declick_button(self.U_Y2_button, 'power', 'U_Y2'), activebackground='#50E24B')
                else:
                    self.U_Y2_button.config(bg='grey90', command=lambda: self.click_button(self.U_Y2_button, 'power', 'U_Y2'), activebackground='grey90')

            self.U_Y2_A = self.client.get_float('Deflectors_XY2_YA')[1]
            self.U_Y2_A_actual.config(text=f'{round(float(self.U_Y2_A),1)} V')
            self.U_Y2_B = self.client.get_float('Deflectors_XY2_YB')[1]
            self.U_Y2_B_actual.config(text=f'{round(float(self.U_Y2_B),1)} V')

            time.sleep(0.1)
    
    def update_U_cat(self):
        self.U_cat_set = float(self.U_cat_entry.get())
        self.U_cat_entry.delete(0, END)
        self.U_cat_entry.insert(0, int(round(self.U_cat_set,0)))
        
        #Write Cathode variable values to server
        if self.U_cat_set >= 0 and self.U_cat_set <= 6500:
            self.client.set_float('Cathode_Voltage_Set', self.U_cat_set)
            print('cathode potential set')
        elif self.U_cat_set < 0:
            self.U_cat_set = self.U_cat
            helpMessage ='Please enter a positive value'
            messageVar = Message(self.cathode, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.25, anchor = CENTER)
            self.cathode.after(5000, messageVar.destroy)
        elif self.U_cat_set > 6500:
            self.U_cat_set = self.U_cat
            helpMessage ='Maximum voltage is 6500'
            messageVar = Message(self.cathode, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.25, anchor = CENTER)
            self.cathode.after(5000, messageVar.destroy)
    
    def update_U_an(self):
        self.U_an_set = float(self.U_an_entry.get())
        self.U_an_entry.delete(0, END)
        self.U_an_entry.insert(0, int(round(self.U_an_set,0)))

        #Write Anode variable values to server
        if self.U_an_set >= 0 and self.U_an_set <= 20000:
            self.client.set_float('Anode_Voltage_Set', self.U_an_set)
            print('anode potential set')
        elif self.U_an_set < 0:
            self.U_an_set = self.U_an
            helpMessage ='Please enter a\n positive value'
            messageVar = Message(self.anode, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.32, rely = 0.28, anchor = CENTER)
            self.anode.after(5000, messageVar.destroy)
        elif self.U_an_set > 20000:
            self.U_an_set = self.U_an
            helpMessage ='Maximum voltage\n is 20000'
            messageVar = Message(self.anode, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.32, rely = 0.28, anchor = CENTER)
            self.anode.after(5000, messageVar.destroy)
    
    def update_I_heat(self):
        self.I_heat_set = float(self.I_heat_entry.get())
        self.I_heat_entry.delete(0, END)
        self.I_heat_entry.insert(0, "{:.2f}".format(self.I_heat_set))
        
        if self.I_heat_set >= 0 and self.I_heat_set <=10:
            self.client.set_float('Cathode_Heater_Current_Set', self.I_heat_set)
            print('cathode heater current set')
        elif self.I_heat_set < 0:
            self.I_heat_set = self.I_heat
            helpMessage ='Please enter a positive value'
            messageVar = Message(self.cathode, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.7, anchor = CENTER)
            self.cathode.after(5000, messageVar.destroy)
        elif self.I_heat_set > 10:
            self.I_heat_set = self.I_heat
            helpMessage ='Maximum current is 10'
            messageVar = Message(self.cathode, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.7, anchor = CENTER)
            self.cathode.after(5000, messageVar.destroy)
    
    def update_t_ion(self):
        self.t_ion_set = float(self.t_ion_entry.get())
        self.t_ion_entry.delete(0, END)
        self.t_ion_entry.insert(0, int(round(self.t_ion_set,0)))
        if self.t_ion_set >= 10 and self.t_ion_set <= 10000:
            self.client.set_float('Drift_Tubes_T_Ion', self.t_ion_set)
            print('ion bake time set')

    def update_t_ext(self):
        self.t_ext_set = float(self.t_ext_entry.get())
        self.t_ext_entry.delete(0, END)
        self.t_ext_entry.insert(0, int(round(self.t_ext_set,0)))
        if self.t_ext_set >= 10 and self.t_ext_set <= 10000:
            self.client.set_float('Drift_Tubes_T_Ext', self.t_ext_set)
            print('ion extract time')

    def update_U_0(self):
        self.U_0_set = float(self.U_0_entry.get())
        self.U_0_entry.delete(0, END)
        self.U_0_entry.insert(0, int(round(self.U_0_set,0)))
        if self.U_0_set >= 0 and self.U_0_set <= 20000:
            self.client.set_float('Drift_Tubes_U0_Set', self.U_0_set)
            print('drift tube potential set')

    def update_U_A(self):
        self.U_A_set = float(self.U_A_entry.get())
        self.U_A_entry.delete(0, END)
        self.U_A_entry.insert(0, round(self.U_A_set,1))
        if self.U_A_set >= 10 and self.U_A_set <= 2000:
            self.client.set_float('Drift_Tubes_UA_Set', self.U_A_set)
            print('drift tube trapping potential')
    
    def update_U_ext(self):
        self.U_ext_set = float(self.U_ext_entry.get())
        self.U_ext_entry.delete(0, END)
        self.U_ext_entry.insert(0, int(round(self.U_ext_set,0)))

        #Write Lens variable values to server
        if self.U_ext_set >= 14 and self.U_ext_set <=10000:
            self.client.set_float('Extraction_Voltage_Set', self.U_ext_set)
            print('extraction lens potential set')
        elif self.U_ext_set < 14:
            self.U_ext_set = self.U_ext
            helpMessage ='Please enter a value greater than 14'
            messageVar = Message(self.lens, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.21, anchor = CENTER)
            self.lens.after(5000, messageVar.destroy)
        elif self.U_ext_set > 10000:
            self.U_ext_set = self.U_ext
            helpMessage ='Please enter a value less than 10000'
            messageVar = Message(self.lens, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.21, anchor = CENTER)
            self.lens.after(5000, messageVar.destroy)

    def update_U_EL1(self):
        self.U_EL1_set = float(self.U_EL1_entry.get())
        self.U_EL1_entry.delete(0, END)
        self.U_EL1_entry.insert(0, int(round(self.U_EL1_set,0)))
        if self.U_EL1_set >= 14 and self.U_EL1_set <= 10000:
            self.client.set_float('Lens_1_Voltage_Set', self.U_EL1_set)
            print('einzel lens 1 potential set')
        elif self.U_EL1_set < 14:
            self.U_EL1_set = self.U_EL1
            helpMessage ='Please enter a value greater than 14'
            messageVar = Message(self.lens, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.21, anchor = CENTER)
            self.lens.after(5000, messageVar.destroy)
        elif self.U_EL1_set > 10000:
            self.U_EL1_set = self.U_EL1
            helpMessage ='Please enter a value less than 10000'
            messageVar = Message(self.lens, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.21, anchor = CENTER)
            self.lens.after(5000, messageVar.destroy)

    def update_U_EL2(self):
        self.U_EL2_set = float(self.U_EL2_entry.get())
        self.U_EL2_entry.delete(0, END)
        self.U_EL2_entry.insert(0, int(round(self.U_EL2_set,0)))
        if self.U_EL2_set >= 14 and self.U_EL2_set <= 10000:
            self.client.set_float('Lens_2_Voltage_Set', self.U_EL2_set)
            print('einzel lens 2 potential set')
        elif self.U_EL2_set < 14:
            self.U_EL2_set = self.U_EL2
            helpMessage ='Please enter a value greater than 14'
            messageVar = Message(self.lens, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.21, anchor = CENTER)
            self.lens.after(5000, messageVar.destroy)
        elif self.U_EL2_set > 10000:
            self.U_EL2_set = self.U_EL2
            helpMessage ='Please enter a value less than 10000'
            messageVar = Message(self.lens, text = helpMessage, font = font_12, width = 600) 
            messageVar.config(bg='firebrick1')
            messageVar.place(relx = 0.5, rely = 0.21, anchor = CENTER)
            self.lens.after(5000, messageVar.destroy)
    
    def update_U_X1(self):
        self.U_X1_set = float(self.U_X1_entry.get())
        self.U_X1_entry.delete(0, END)
        self.U_X1_entry.insert(0, round(self.U_X1_set,1))
        if abs(self.U_X1_set) <= 1000:
            self.client.set_float('Deflectors_XY1_X_Set', self.U_X1_set)
            print('X1 deflector potential set')

    def update_U_Y1(self):
        self.U_Y1_set = float(self.U_Y1_entry.get())
        self.U_Y1_entry.delete(0, END)
        self.U_Y1_entry.insert(0, round(self.U_Y1_set,1))
        if abs(self.U_Y1_set) <= 1000:
            self.client.set_float('Deflectors_XY1_Y_Set', self.U_Y1_set)
            print('Y1 deflector potential set')

    def update_U_X2(self):
        self.U_X2_set = float(self.U_X2_entry.get())
        self.U_X2_entry.delete(0, END)
        self.U_X2_entry.insert(0, round(self.U_X2_set,1))
        if abs(self.U_X2_set) <= 1000:
            self.client.set_float('Deflectors_XY2_X_Set', self.U_X2_set)
            print('X2 deflector potential set')

    def update_U_Y2(self):
        self.U_Y2_set = float(self.U_Y2_entry.get())
        self.U_Y2_entry.delete(0, END)
        self.U_Y2_entry.insert(0, round(self.U_Y2_set,1))
        if abs(self.U_Y2_set) <= 1000:
            self.client.set_float('Deflectors_XY2_Y_Set', self.U_Y2_set)
            print('Y2 deflector potential set')


    
    #Creates the Different Menus in the Main Window
    def createMenus(self, menu):
        #Creates File menu
        self.filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=self.filemenu)
        #filemenu.add_command(label="Import", command=lambda: self.askopenfile(), accelerator="Ctrl+I")
        #filemenu.add_command(label="Save", command=lambda: CSA.saveGraph(), accelerator="Ctrl+S")
        #filemenu.add_command(label='Settings', command=lambda: self.Settings())
        #filemenu.add_command(label='Calibrate', command=lambda: self.calibration())
        self.filemenu.add_separator()
        self.filemenu.add_command(label='New Window', command=lambda: startProgram(Toplevel(self.root)))
        self.filemenu.add_command(label='Exit', command=lambda: self.quitProgram())

        #Creates Help menu
        self.helpmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=self.helpmenu)
        self.helpmenu.add_command(label='Instructions', command= lambda: self.Instructions())
        self.helpmenu.add_command(label='About', command= lambda: self.About())

    #Creates Different Tabs in the Main Window
    def createTabs(self):
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=font_16)
        style.configure('TFrame', background='#96CAF2')
        #style.configure('TFrame', background='#F5974F')
        self.tabControl = ttk.Notebook(self.root)
        self.service_tab = ttk.Frame(self.tabControl)
        self.source_tab = ttk.Frame(self.tabControl)
        self.slit_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.service_tab, text='Service')
        self.tabControl.add(self.source_tab, text='Source')
        self.tabControl.add(self.slit_tab, text='Slit')
        self.tabControl.pack(expand=1, fill='both')
        #self.tabControl.place(relx=0.5, rely=0, anchor=N)


    #Creates the Cathode Controls in a frame that is placed at the coordinates (x, y)
    def cathode_controls(self, x, y):    
        self.cathode = Frame(self.service_tab, width = 400, height = 200, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.cathode.place(relx = x, rely = y, anchor = CENTER)
 
        #Canvas for creating divider line between potential and current controls
        w = Canvas(self.cathode, width=390, height=2, bg='grey90', highlightthickness=0)
        w.create_line(0, 1, 390, 1)
        w.place(relx=0.5,rely=0.55,anchor=CENTER)

        cathodeLabel = Label(self.cathode, text = 'Cathode', font = font_18, bg = 'grey90', fg = 'black')
        cathodeLabel.place(relx=0.5, rely=0.1, anchor = CENTER)

        self.U_cat_button = Button(self.cathode, image=self.power_button, command=lambda: self.click_button(self.U_cat_button, 'power', 'U_cat'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_cat_button.place(relx=0.1, rely=0.25, anchor=CENTER)

        U_cat_label1 = Label(self.cathode, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_cat_label1.place(relx=0.15, rely=0.42, anchor=CENTER)
        #Creates subscript "cat" because Tkinter is stupid and doesn't support rich text in Labels
        U_cat_label2 = Label(self.cathode, text='cat', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_cat_label2.place(relx=0.165, rely=0.45, anchor=W)

        U_cat_label3 = Label(self.cathode, text='= -', font=font_14, bg = 'grey90', fg = 'black')
        U_cat_label3.place(relx=0.29, rely=0.42, anchor=E)

        self.U_cat_entry = Entry(self.cathode, font=font_14, justify=RIGHT)
        self.U_cat_entry.insert(0,int(round(self.U_cat,0)))
        self.U_cat_entry.place(relx=0.29, rely=0.42, anchor=W, width=70)
        self.U_cat_entry.bind("<Return>", lambda eff: self.update_U_cat())

        U_cat_label4 = Label(self.cathode, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_cat_label4.place(relx=0.49, rely=0.42, anchor=CENTER)

        self.U_cat_actual = Label(self.cathode, text=f'-{round(self.U_cat,0)} V', font=font_14, bg='grey90', fg='black')
        self.U_cat_actual.place(relx=0.72, rely=0.42, anchor=E)

        self.I_cat_label = Label(self.cathode, text=f'{round(self.I_cat,1)} mA', font=font_14, bg='grey90', fg='black')
        self.I_cat_label.place(relx=0.98, rely=0.42, anchor=E)

        self.I_heat_button = Button(self.cathode, image=self.power_button, command=lambda: self.click_button(self.I_heat_button, 'power', 'I_heat'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.I_heat_button.place(relx=0.1, rely=0.7, anchor=CENTER)

        I_heat_label1 = Label(self.cathode, text='I', font=font_14, bg = 'grey90', fg = 'black')
        I_heat_label1.place(relx=0.155, rely=0.87, anchor=CENTER)
        #Creates subscript "heat" because Tkinter is stupid and doesn't support rich text in Labels
        I_heat_label2 = Label(self.cathode, text='heat', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        I_heat_label2.place(relx=0.16, rely=0.9, anchor=W)

        I_heat_label3 = Label(self.cathode, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        I_heat_label3.place(relx=0.28, rely=0.87, anchor=E)

        self.I_heat_entry = Entry(self.cathode, font=font_14, justify=RIGHT)
        self.I_heat_entry.insert(0, round(self.I_heat,2))
        self.I_heat_entry.place(relx=0.29, rely=0.87, anchor=W, width=70)
        I_heat_label4 = Label(self.cathode, text='A', font=font_14, bg = 'grey90', fg = 'black')
        I_heat_label4.place(relx=0.49, rely=0.87, anchor=CENTER)
        self.I_heat_entry.bind("<Return>", lambda eff: self.update_I_heat())

        self.I_heat_actual = Label(self.cathode, text='{:.2f}'.format(self.I_heat)+' A', font=font_14, bg='grey90', fg='black')
        self.I_heat_actual.place(relx=0.72, rely=0.87, anchor=E)

        U_filament = Label(self.cathode, text=f'{round(self.U_filament,2)} V', font=font_14, bg='grey90', fg='black')
        U_filament.place(relx=0.98, rely=0.87, anchor=E)

        
    #Creates the Anode Controls in a frame that is placed at the coordinates (x, y)
    def anode_controls(self, x, y):
        self.anode = Frame(self.service_tab, width = 400, height = 200, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.anode.place(relx = x, rely = y, anchor = CENTER)

        anodeLabel = Label(self.anode, text = 'Anode', font = font_18, bg = 'grey90', fg = 'black')
        anodeLabel.place(relx=0.3, rely=0.1, anchor = CENTER)

        self.anode_button = Button(self.anode, image=self.power_button, command=lambda: self.click_button(self.anode_button, 'power', 'anode_power'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.anode_button.place(relx=0.1, rely=0.25, anchor=CENTER)

        U_an_label1 = Label(self.anode, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_an_label1.place(relx=0.1, rely=0.49, anchor=CENTER)
        #Creates subscript "An" because Tkinter is stupid and doesn't support rich text in Labels
        U_an_label2 = Label(self.anode, text='An', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_an_label2.place(relx=0.115, rely=0.52, anchor=W)

        U_an_label3 = Label(self.anode, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_an_label3.place(relx=0.24, rely=0.49, anchor=E)

        self.U_an_entry = Entry(self.anode, font=font_14, justify=RIGHT)
        self.U_an_entry.place(relx=0.24, rely=0.49, anchor=W, width=70)
        self.U_an_entry.insert(0,int(round(self.U_an,0)))
        self.U_an_entry.bind("<Return>", lambda eff: self.update_U_an())

        U_an_label4 = Label(self.anode, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_an_label4.place(relx=0.44, rely=0.49, anchor=CENTER)

        U_an__actual_label1 = Label(self.anode, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_an__actual_label1.place(relx=0.1, rely=0.67, anchor=CENTER)
        #Creates subscript "An" because Tkinter is stupid and doesn't support rich text in Labels
        U_an__actual_label2 = Label(self.anode, text='An', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_an__actual_label2.place(relx=0.115, rely=0.7, anchor=W)

        U_an__actual_label3 = Label(self.anode, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_an__actual_label3.place(relx=0.24, rely=0.67, anchor=E)

        self.U_an_actual_label4 = Label(self.anode, text=f'{round(self.U_an,0)}', font=font_14, bg='grey90', fg='black')
        self.U_an_actual_label4.place(relx=0.42, rely=0.67, anchor=E)

        U_an_actual_label5 = Label(self.anode, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_an_actual_label5.place(relx=0.44, rely=0.67, anchor=CENTER)

        I_an_label1 = Label(self.anode, text='I', font=font_14, bg = 'grey90', fg = 'black')
        I_an_label1.place(relx=0.105, rely=0.85, anchor=CENTER)
        #Creates subscript "An" because Tkinter is stupid and doesn't support rich text in Labels
        I_an_label2 = Label(self.anode, text='An', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        I_an_label2.place(relx=0.115, rely=0.88, anchor=W)

        I_an_label3 = Label(self.anode, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        I_an_label3.place(relx=0.24, rely=0.85, anchor=E)

        self.I_an_label4 = Label(self.anode, text=f'{round(self.I_an,0)}', font=font_14, bg='grey90', fg='black')
        self.I_an_label4.place(relx=0.395, rely=0.85, anchor=E)

        I_an_label5 = Label(self.anode, text='μA', font=font_14, bg = 'grey90', fg = 'black')
        I_an_label5.place(relx=0.43, rely=0.85, anchor=CENTER)


        self.anode_fig = Figure(figsize=(2,1.9))
        self.anode_ax = self.anode_fig.add_subplot(111)
        freqPlot = FigureCanvasTkAgg(self.anode_fig, self.anode)
        freqPlot.get_tk_widget().place(relx=0.99, rely=0.98, anchor=SE)
        self.anode_fig.patch.set_facecolor("#E5E5E5")
        self.anode_ax.axes.set_facecolor(color='#E5E5E5')
        self.anode_ax.axes.xaxis.set_visible(False)
        self.anode_ax.set_ylim(0,10000)
        self.anode_fig.tight_layout()
        self.anode_ani = animation.FuncAnimation(self.anode_fig, self.animate, interval = 500)


    #Creates the Drift Tube Controls in a frame that is placed at the coordinates (x, y)
    def drift_tube_controls(self, x, y):
        self.dt = Frame(self.service_tab, width = 400, height = 200, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.dt.place(relx = x, rely = y, anchor = CENTER)

        dtLabel = Label(self.dt, text = 'Drift Tubes', font = font_18, bg = 'grey90', fg = 'black')
        dtLabel.place(relx=0.5, rely=0.1, anchor = CENTER)

        self.dt_button = Button(self.dt, image=self.power_button, command=lambda: self.click_button(self.dt_button, 'power', 'dt_power'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.dt_button.place(relx=0.1, rely=0.2, anchor=CENTER)

        self.dt_timer_button = Button(self.dt, text='Timer OFF', relief = 'raised', command=lambda: self.click_button(self.dt_timer_button, 'timer'), width=8, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.dt_timer_button.place(relx=0.25, rely=0.25, anchor=CENTER)

        t_ion_label1 = Label(self.dt, text='t', font=font_14, bg='grey90', fg='black')
        t_ion_label1.place(relx=0.4, rely=0.25, anchor=CENTER)
        t_ion_label2 = Label(self.dt, text='ion', font=('Helvetica', 8), bg='grey90', fg='black')
        t_ion_label2.place(relx=0.407, rely=0.28, anchor=W)

        self.t_ion_entry = Entry(self.dt, font=font_14, justify=RIGHT)
        self.t_ion_entry.place(relx=0.46, rely=0.25, anchor=W, width=50)
        self.t_ion_entry.insert(0,str(self.t_ion))
        self.t_ion_entry.bind("<Return>", lambda eff: self.update_t_ion())

        t_ion_label3 = Label(self.dt, text='ms', font=font_14, bg='grey90', fg='black')
        t_ion_label3.place(relx=0.63, rely=0.25, anchor=CENTER)

        t_ext_label1 = Label(self.dt, text='t', font=font_14, bg='grey90', fg='black')
        t_ext_label1.place(relx=0.73, rely=0.25, anchor=CENTER)
        t_ext_label2 = Label(self.dt, text='ext', font=('Helvetica', 8), bg='grey90', fg='black')
        t_ext_label2.place(relx=0.737, rely=0.28, anchor=W)

        self.t_ext_entry = Entry(self.dt, font=font_14, justify=RIGHT)
        self.t_ext_entry.place(relx=0.79, rely=0.25, anchor=W, width=50)
        self.t_ext_entry.insert(0,str(self.t_ext))
        self.t_ext_entry.bind("<Return>", lambda eff: self.update_t_ext())

        t_ext_label3 = Label(self.dt, text='ms', font=font_14, bg='grey90', fg='black')
        t_ext_label3.place(relx=0.96, rely=0.25, anchor=CENTER)

        #Canvas for creating divider line between pulse-timer and drift tube potentials
        w = Canvas(self.dt, width=390, height=2, bg='grey90', highlightthickness=0)
        w.create_line(0, 1, 390, 1)
        w.place(relx=0.5,rely=0.35,anchor=CENTER)


        self.I_dt_label = Label(self.dt, text=f'{int(round(self.I_dt,0))} μA', font=font_14, bg = 'grey90', fg = 'black')
        self.I_dt_label.place(relx=0.98, rely=0.45, anchor=E)


        #Drift Tube Potentials
        U_0_label1 = Label(self.dt, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_0_label1.place(relx=0.1, rely=0.45, anchor=CENTER)
        #Creates subscript "0" because Tkinter is stupid and doesn't support rich text in Labels
        U_0_label2 = Label(self.dt, text='0', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=1)
        U_0_label2.place(relx=0.115, rely=0.48, anchor=W)

        U_0_label3 = Label(self.dt, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_0_label3.place(relx=0.225, rely=0.45, anchor=E)

        self.U_0_entry = Entry(self.dt, font=font_14, justify=RIGHT)
        self.U_0_entry.place(relx=0.24, rely=0.45, anchor=W, width=70)
        self.U_0_entry.insert(0,str(self.U_0))
        self.U_0_entry.bind("<Return>", lambda eff: self.update_U_0())



        U_0_label4 = Label(self.dt, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_0_label4.place(relx=0.44, rely=0.45, anchor=CENTER)

        self.U_0_actual = Label(self.dt, text=f'{round(self.U_0,0)} V', font=font_14, bg='grey90', fg='black')
        self.U_0_actual.place(relx=0.7, rely=0.45, anchor=E)

        U_A_label1 = Label(self.dt, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_A_label1.place(relx=0.1, rely=0.6, anchor=CENTER)
        #Creates subscript "A" because Tkinter is stupid and doesn't support rich text in Labels
        U_A_label2 = Label(self.dt, text='A', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=1)
        U_A_label2.place(relx=0.115, rely=0.63, anchor=W)

        U_A_label3 = Label(self.dt, text='= -', font=font_14, bg = 'grey90', fg = 'black')
        U_A_label3.place(relx=0.24, rely=0.6, anchor=E)

        self.U_A_entry = Entry(self.dt, font=font_14, justify=RIGHT)
        self.U_A_entry.place(relx=0.24, rely=0.6, anchor=W, width=70)
        self.U_A_entry.insert(0,"{:.1f}".format(self.U_A))
        self.U_A_entry.bind("<Return>", lambda eff: self.update_U_A())

        U_A_label4 = Label(self.dt, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_A_label4.place(relx=0.44, rely=0.6, anchor=CENTER)
        
        self.U_A_actual = Label(self.dt, text="-{:.1f} V".format(self.U_A), font=font_14, bg='grey90', fg='black')
        self.U_A_actual.place(relx=0.7, rely=0.6, anchor=E)
        

        U_B1_label1 = Label(self.dt, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_B1_label1.place(relx=0.105, rely=0.75, anchor=CENTER)
        #Creates subscript "B1" because Tkinter is stupid and doesn't support rich text in Labels
        U_B1_label2 = Label(self.dt, text='B1', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_B1_label2.place(relx=0.12, rely=0.78, anchor=W)

        U_B1_label3 = Label(self.dt, text='= -', font=font_14, bg = 'grey90', fg = 'black')
        U_B1_label3.place(relx=0.24, rely=0.75, anchor=E)

        self.U_B1_entry = Entry(self.dt, font=font_14, justify=RIGHT)
        self.U_B1_entry.place(relx=0.24, rely=0.75, anchor=W, width=70)
        self.U_B1_entry.insert(0,"{:.1f}".format(self.U_B1))
        #self.U_B1_entry.bind("<Return>", lambda eff: self.update_U_B1())

        U_B1_label5 = Label(self.dt, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_B1_label5.place(relx=0.44, rely=0.75, anchor=CENTER)



        U_B2_label1 = Label(self.dt, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_B2_label1.place(relx=0.105, rely=0.9, anchor=CENTER)
        #Creates subscript "B2" because Tkinter is stupid and doesn't support rich text in Labels
        U_B2_label2 = Label(self.dt, text='B2', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_B2_label2.place(relx=0.12, rely=0.93, anchor=W)

        U_B2_label3 = Label(self.dt, text='= -', font=font_14, bg = 'grey90', fg = 'black')
        U_B2_label3.place(relx=0.24, rely=0.9, anchor=E)

        self.U_B2_entry = Entry(self.dt, font=font_14, justify=RIGHT)
        self.U_B2_entry.place(relx=0.24, rely=0.9, anchor=W, width=70)
        self.U_B2_entry.insert(0,"{:.1f}".format(self.U_B2))
        #self.U_B1_entry.bind("<Return>", lambda eff: self.update_U_B2())

        U_B2_label5 = Label(self.dt, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_B2_label5.place(relx=0.44, rely=0.9, anchor=CENTER)


        U_B_label1 = Label(self.dt, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_B_label1.place(relx=0.65, rely=0.825, anchor=CENTER)
        U_B_label2 = Label(self.dt, text='B', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=1)
        U_B_label2.place(relx=0.665, rely=0.855, anchor=W)
        U_B_label3 = Label(self.dt, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_B_label3.place(relx=0.765, rely=0.825, anchor=E)
        self.U_B_actual = Label(self.dt, text="-{:.1f} V".format(self.U_B), font=font_14, bg = 'grey90', fg = 'black')
        self.U_B_actual.place(relx=0.98, rely=0.825, anchor=E)

    #Creates the Lens Controls in a frame that is placed at the coordinates (x,y)
    def lens_controls(self, x, y):
        self.lens = Frame(self.service_tab, width = 400, height = 200, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.lens.place(relx = x, rely = y, anchor = CENTER)

        lensLabel = Label(self.lens, text = 'Lens', font = font_18, bg = 'grey90', fg = 'black')
        lensLabel.place(relx=0.5, rely=0.1, anchor = CENTER)

        self.U_ext_button = Button(self.lens, image=self.power_button, command=lambda: self.click_button(self.U_ext_button, 'power', 'U_ext'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_ext_button.place(relx=0.1, rely=0.35, anchor=CENTER)

        U_ext_label1 = Label(self.lens, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_ext_label1.place(relx=0.35, rely=0.35, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_ext_label2 = Label(self.lens, text='ext', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_ext_label2.place(relx=0.365, rely=0.38, anchor=W)

        U_ext_label3 = Label(self.lens, text='= -', font=font_14, bg = 'grey90', fg = 'black')
        U_ext_label3.place(relx=0.49, rely=0.35, anchor=E)

        self.U_ext_entry = Entry(self.lens, font=font_14, justify=RIGHT)
        self.U_ext_entry.place(relx=0.49, rely=0.35, anchor=W, width=70)
        self.U_ext_entry.insert(0,str(self.U_ext))
        self.U_ext_entry.bind("<Return>", lambda eff: self.update_U_ext())

        U_ext_label4 = Label(self.lens, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_ext_label4.place(relx=0.69, rely=0.35, anchor=CENTER)

        self.U_ext_actual = Label(self.lens, text=f'{round(self.U_ext,0)} V', font=font_14, bg='grey90', fg='black')
        self.U_ext_actual.place(relx=0.98, rely=0.35, anchor=E)


        self.U_EL1_button = Button(self.lens, image=self.power_button, command=lambda: self.click_button(self.U_EL1_button, 'power', 'U_EL1'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_EL1_button.place(relx=0.1, rely=0.6, anchor=CENTER)

        self.U_EL1_charge = Button(self.lens, text='positive', relief = 'raised', command=lambda: self.click_button(self.U_EL1_charge, 'charge', 'U_EL1_charge', self.U_EL1_label3), width=6, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.U_EL1_charge.place(relx=0.25, rely=0.6, anchor=CENTER)

        U_EL1_label1 = Label(self.lens, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_EL1_label1.place(relx=0.35, rely=0.6, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_EL1_label2 = Label(self.lens, text='EL1', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_EL1_label2.place(relx=0.365, rely=0.63, anchor=W)

        self.U_EL1_label3 = Label(self.lens, text='=  ', font=font_14, bg = 'grey90', fg = 'black')
        self.U_EL1_label3.place(relx=0.49, rely=0.6, anchor=E)

        self.U_EL1_entry = Entry(self.lens, font=font_14, justify=RIGHT)
        self.U_EL1_entry.place(relx=0.49, rely=0.6, anchor=W, width=70)
        self.U_EL1_entry.insert(0,str(self.U_EL1))
        self.U_EL1_entry.bind("<Return>", lambda eff: self.update_U_EL1())

        U_EL1_label4 = Label(self.lens, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_EL1_label4.place(relx=0.69, rely=0.6, anchor=CENTER)

        self.U_EL1_actual = Label(self.lens, text=f'{round(self.U_EL1_q*self.U_EL1,0)} V', font=font_14, bg='grey90', fg='black')
        self.U_EL1_actual.place(relx=0.98, rely=0.6, anchor=E)


        self.U_EL2_button = Button(self.lens, image=self.power_button, command=lambda: self.click_button(self.U_EL2_button, 'power', 'U_EL2'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_EL2_button.place(relx=0.1, rely=0.85, anchor=CENTER)

        self.U_EL2_charge = Button(self.lens, text='positive', relief = 'raised', command=lambda: self.click_button(self.U_EL2_charge, 'charge', 'U_EL2_charge', self.U_EL2_label3), width=6, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.U_EL2_charge.place(relx=0.25, rely=0.85, anchor=CENTER)

        U_EL2_label1 = Label(self.lens, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_EL2_label1.place(relx=0.35, rely=0.85, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_EL2_label2 = Label(self.lens, text='EL2', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_EL2_label2.place(relx=0.365, rely=0.88, anchor=W)

        self.U_EL2_label3 = Label(self.lens, text='=  ', font=font_14, bg = 'grey90', fg = 'black')
        self.U_EL2_label3.place(relx=0.49, rely=0.85, anchor=E)

        self.U_EL2_entry = Entry(self.lens, font=font_14, justify=RIGHT)
        self.U_EL2_entry.place(relx=0.49, rely=0.85, anchor=W, width=70)
        self.U_EL2_entry.insert(0,str(self.U_EL2))
        self.U_EL2_entry.bind("<Return>", lambda eff: self.update_U_EL2())

        U_EL2_label4 = Label(self.lens, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_EL2_label4.place(relx=0.69, rely=0.85, anchor=CENTER)

        self.U_EL2_actual = Label(self.lens, text=f'{round(self.U_EL2,0)} V', font=font_14, bg='grey90', fg='black')
        self.U_EL2_actual.place(relx=0.98, rely=0.85, anchor=E)


    def deflector_controls(self, x, y):
        self.deflector = Frame(self.service_tab, width = 400, height = 200, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.deflector.place(relx = x, rely = y, anchor = CENTER)

        deflectorLabel = Label(self.deflector, text = 'Deflectors', font = font_18, bg = 'grey90', fg = 'black')
        deflectorLabel.place(relx=0.35, rely=0.1, anchor = CENTER)

        ALabel = Label(self.deflector, text = 'A:', font = font_14, bg = 'grey90', fg = 'black')
        ALabel.place(relx=0.67, rely=0.15, anchor = CENTER)

        BLabel = Label(self.deflector, text = 'B:', font = font_14, bg = 'grey90', fg = 'black')
        BLabel.place(relx=0.9, rely=0.15, anchor = CENTER)

        self.U_X1_button = Button(self.deflector, image=self.power_button, command=lambda: self.click_button(self.U_X1_button, 'power', 'U_X1'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_X1_button.place(relx=0.1, rely=0.3, anchor=CENTER)

        U_X1_label1 = Label(self.deflector, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_X1_label1.place(relx=0.2, rely=0.3, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_X1_label2 = Label(self.deflector, text='X1', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_X1_label2.place(relx=0.215, rely=0.33, anchor=W)

        U_X1_label3 = Label(self.deflector, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_X1_label3.place(relx=0.32, rely=0.3, anchor=E)

        self.U_X1_entry = Entry(self.deflector, font=font_14, justify=RIGHT)
        self.U_X1_entry.place(relx=0.32, rely=0.3, anchor=W, width=60)
        self.U_X1_entry.insert(0, round(float(self.U_X1_A),1))
        self.U_X1_entry.bind("<Return>", lambda eff: self.update_U_X1())

        U_X1_label4 = Label(self.deflector, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_X1_label4.place(relx=0.49, rely=0.3, anchor=CENTER)

        self.U_X1_A_actual = Label(self.deflector, text=f'{round(float(self.U_X1_A),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_X1_A_actual.place(relx=0.75, rely=0.3, anchor=E)

        self.U_X1_B_actual = Label(self.deflector, text=f'{round(float(self.U_X1_B),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_X1_B_actual.place(relx=0.98, rely=0.3, anchor=E)


        self.U_Y1_button = Button(self.deflector, image=self.power_button, command=lambda: self.click_button(self.U_Y1_button, 'power', 'U_Y1'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_Y1_button.place(relx=0.1, rely=0.5, anchor=CENTER)

        U_Y1_label1 = Label(self.deflector, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_Y1_label1.place(relx=0.2, rely=0.5, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_Y1_label2 = Label(self.deflector, text='Y1', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_Y1_label2.place(relx=0.215, rely=0.53, anchor=W)

        U_Y1_label3 = Label(self.deflector, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_Y1_label3.place(relx=0.32, rely=0.5, anchor=E)

        self.U_Y1_entry = Entry(self.deflector, font=font_14, justify=RIGHT)
        self.U_Y1_entry.place(relx=0.32, rely=0.5, anchor=W, width=60)
        self.U_Y1_entry.insert(0, round(float(self.U_Y1_A),1))
        self.U_Y1_entry.bind("<Return>", lambda eff: self.update_U_Y1())

        U_Y1_label4 = Label(self.deflector, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_Y1_label4.place(relx=0.49, rely=0.5, anchor=CENTER)

        self.U_Y1_A_actual = Label(self.deflector, text=f'{round(float(self.U_Y1_A),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_Y1_A_actual.place(relx=0.75, rely=0.5, anchor=E)

        self.U_Y1_B_actual = Label(self.deflector, text=f'{round(float(self.U_Y1_B),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_Y1_B_actual.place(relx=0.98, rely=0.5, anchor=E)


        self.U_X2_button = Button(self.deflector, image=self.power_button, command=lambda: self.click_button(self.U_X2_button, 'power', 'U_X2'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_X2_button.place(relx=0.1, rely=0.7, anchor=CENTER)

        U_X2_label1 = Label(self.deflector, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_X2_label1.place(relx=0.2, rely=0.7, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_X2_label2 = Label(self.deflector, text='X2', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_X2_label2.place(relx=0.215, rely=0.73, anchor=W)

        U_X2_label3 = Label(self.deflector, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_X2_label3.place(relx=0.32, rely=0.7, anchor=E)

        self.U_X2_entry = Entry(self.deflector, font=font_14, justify=RIGHT)
        self.U_X2_entry.place(relx=0.32, rely=0.7, anchor=W, width=60)
        self.U_X2_entry.insert(0, round(float(self.U_X2_A),1))
        self.U_X2_entry.bind("<Return>", lambda eff: self.update_U_X2())

        U_X2_label4 = Label(self.deflector, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_X2_label4.place(relx=0.49, rely=0.7, anchor=CENTER)

        self.U_X2_A_actual = Label(self.deflector, text=f'{round(float(self.U_X2_A),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_X2_A_actual.place(relx=0.75, rely=0.7, anchor=E)

        self.U_X2_B_actual = Label(self.deflector, text=f'{round(float(self.U_X2_B),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_X2_B_actual.place(relx=0.98, rely=0.7, anchor=E)


        self.U_Y2_button = Button(self.deflector, image=self.power_button, command=lambda: self.click_button(self.U_Y2_button, 'power', 'U_Y2'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.U_Y2_button.place(relx=0.1, rely=0.9, anchor=CENTER)

        U_Y2_label1 = Label(self.deflector, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_Y2_label1.place(relx=0.2, rely=0.9, anchor=CENTER)
        #Creates subscript "ext" because Tkinter is stupid and doesn't support rich text in Labels
        U_Y2_label2 = Label(self.deflector, text='Y2', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=3)
        U_Y2_label2.place(relx=0.215, rely=0.93, anchor=W)

        U_Y2_label3 = Label(self.deflector, text='= ', font=font_14, bg = 'grey90', fg = 'black')
        U_Y2_label3.place(relx=0.32, rely=0.9, anchor=E)

        self.U_Y2_entry = Entry(self.deflector, font=font_14, justify=RIGHT)
        self.U_Y2_entry.place(relx=0.32, rely=0.9, anchor=W, width=60)
        self.U_Y2_entry.insert(0, round(float(self.U_Y2_A),1))
        self.U_Y2_entry.bind("<Return>", lambda eff: self.update_U_Y2())

        U_Y2_label4 = Label(self.deflector, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_Y2_label4.place(relx=0.49, rely=0.9, anchor=CENTER)

        self.U_Y2_A_actual = Label(self.deflector, text=f'{round(float(self.U_Y2_A),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_Y2_A_actual.place(relx=0.75, rely=0.9, anchor=E)

        self.U_Y2_B_actual = Label(self.deflector, text=f'{round(float(self.U_Y2_B),1)} V', font=font_14, bg='grey90', fg='black')
        self.U_Y2_B_actual.place(relx=0.98, rely=0.9, anchor=E)

    def gas_valve(self, x, y):
        self.gas = Frame(self.service_tab, width = 400, height = 200, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.gas.place(relx = x, rely = y, anchor = CENTER)

        gasLabel = Label(self.gas, text = 'Gas Valve', font = font_18, bg = 'grey90', fg = 'black')
        gasLabel.place(relx=0.3, rely=0.1, anchor = CENTER)
        

    def makeGui(self, root=None):
        if root == None:
            self.root = Tk()
        else:
            self.root = root

        menu = Menu(self.root)
        self.root.config(menu=menu)

        self.root.title("CUEBIT Control Center")
        self.root.geometry("1920x1050")
        self.root.configure(bg='white')
        self.root.protocol("WM_DELETE_WINDOW", self.quitProgram)
        if platform.system() == 'Windows':
            try:
                self.root.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')

        try:
            image = Image.open('images/power-button.png')
        except:
            image = Image.open('C:/Users/cuebit-control/Downloads/CUEBIT-Control-Interface-main/images/power-button.png')
        image = image.resize((30,32), Image.ANTIALIAS)
        self.power_button = ImageTk.PhotoImage(image)

        self.createMenus(menu)
        self.createTabs()
        self.cathode_controls(0.12, 0.12)
        self.drift_tube_controls(0.12, 0.35)
        '''
        self.cathode_controls(0.12, 0.81)
        '''
        self.anode_controls(0.35, 0.12)
        self.lens_controls(0.35, 0.35)
        self.deflector_controls(0.12, 0.58)
        self.gas_valve(0.35, 0.58)

        multiThreading(self.data_reader)
        self.root.mainloop()


startProgram()
        

