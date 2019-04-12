# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:04:15 2019

@author: bkontou
"""

import tkinter as tk
from tkinter import filedialog
#import test
import obspy as op
import os
import numpy as np
import pandas as pd

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from windows import *
from event import Event

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
            
    def Label(self, text, row=1, column=1, padx=0, pady=0):
        label = tk.Label(self, text=text)
        label.grid(row=row, column=column, padx=padx, pady=pady)
        label.bind("<1>", self.quit)
        return label
        
    def Button(self, text, f, row=1, column=1, padx=0, pady=0):
        button = tk.Button(self, text=text, command=f)
        button.grid(row=row, column=column, padx=padx, pady=pady)
        return button
        
    def Entry(self, row=1, column=1, width=10, padx=0, pady=0):
        entry = tk.Entry(self, width=width)
        entry.grid(row=row, column=column, padx=padx, pady=pady)
        return entry
    
    def Checkbutton(self, var, text, row=1, column=1, padx=0, pady=0):
        cb = tk.Checkbutton(self, text=text, variable=var)
        cb.grid(row=row, column=column, padx=padx, pady=pady)
        return cb
    
    def OptionMenu(self, tkvar, choices, row=1, column=1, padx=0, pady=0):
        om = tk.OptionMenu(self, tkvar, *choices)
        om.grid(row=row, column=column, padx=padx, pady=pady) 
        return om
        
class MainWindow(MainApplication):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.popup = tk.Toplevel()
        self.wfs = WaveformWindow(self.popup)
        self.wfs.pack(side="top", fill="both", expand=True)
                
        self.popup.protocol("WM_DELETE_WINDOW", self.wfs.on_closing)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        self.closed = 0
        
        self.winfo_toplevel().title("Pick Viewer")
        
        #Members#
        self.pick_df = pd.DataFrame()
        self.orid_df = pd.DataFrame()
        self.orid_checklist = pd.DataFrame.from_dict({'orid':[],'correct':[]})
        
        self.orid_list = []
        self.Npicks = len(self.pick_df)
        self.N = 0
        self.pick_info = {}
        
        self.current_event_status = False
        
        self.evList = []
        
        ###CHANGE THIS###
        self.path = '/Users/pgcseismolab/Documents/'
        
        #info
        self.p_date = "None"
        self.p_id = "None"

        self.P_cha = "HHZ"
        self.S_cha = "HHE"
        
        #Widgets#
        self.wf_B = self.Button('view waveform', f=self.show_window)
        
        self.next_B = self.Button('next',f=self.scrollDown,row=2, column=3)
        self.prev_B = self.Button('prev',f=self.scrollUp,row=2,column=0)
        
        self.Label("picks csv",row=2,column=1)
        self.csv_E = self.Entry(row=3,column=1,width=50, pady=10)
        self.FB = self.Button("Choose File",f=self.FileWindow, row=3,column=2)
        self.read_B = self.Button("read", f=self.loadDF, row=4)
        
        self.time_L = self.Label(self.p_date, row=5)
        self.id_L = self.Label(self.p_id, row=6)
        
        self.CB_var = tk.IntVar()
        self.goodev_CB = self.Checkbutton(self.CB_var, 'Correct', row=7, column=2)
        
        self.save_B = self.Button("Save", f=self.saveOut, row=7,column=0)
        #self.goodev_CB.configure(state='disable')
        
        
    def loadDF(self):
        self.pick_df = pd.read_csv(self.csv_E.get())
        self.pick_df = self.pick_df.sort_values('orid')
        self.orid_list = self.pick_df.orid.unique()
        self.orid_checklist.orid = [0]*len(self.orid_list)
        
        
        #update eventlist
        for orid in self.orid_list:
            self.evList.append(Event(self.pick_df[self.pick_df.orid == orid]))
            
        
        self.Npicks = len(self.orid_list)
        self.N = 0
    
    def FileWindow(self, event=None):
        self.csv_E.delete(0,'end')
        filename = filedialog.askopenfilename()
        self.csv_E.insert(0,filename)
        

            
    def updateInfo(self):
        self.time_L.config(text=self.evList[self.N].time)
        self.id_L.config(text=self.evList[self.N].orid)
        self.current_event_status = self.evList[self.N].status
        if self.current_event_status == True:
            self.goodev_CB.select()
        else:
            self.goodev_CB.deselect()

    
    def scrollUp(self):
        self.evList[self.N].status = self.CB_var.get()
        self.N = (self.N - 1)%self.Npicks
        self.updateInfo()

        self.show_window()
    
    def scrollDown(self):
        self.evList[self.N].status = self.CB_var.get()
        self.N = (self.N + 1)%self.Npicks
        self.updateInfo()
        
        self.show_window()
        
    def saveOut(self):
        for index,i in enumerate(self.orid_list):
            self.orid_checklist.iloc[index] = i, bool(self.evList[self.evList.index(i)].status)
        
        self.orid_checklist.to_csv('%s-out.csv' % self.csv_E.get())

    
    def Debug(self):
        print(self.pick_df)
        
    def show_window(self):

        self.popup.update()
        self.popup.deiconify()
        self.wfs.plot(self.evList[self.N].evInfo, self.path)
        self.wfs.plot(self.evList[self.N].evInfo, self.path)
        
    def on_close(self):
        self.closed = 1
        #self.quit()
        
if __name__ == '__main__':
    running = True
    root = tk.Tk()
    MA = MainWindow(root)
    MA.pack(side="top", fill="both", expand=True)
    
    while running:
        root.update()
        if MA.closed:
            root.destroy()
            running = 0
    #root.mainloop()