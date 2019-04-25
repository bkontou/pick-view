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
from functools import partial

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
        self.test = "AAAAAAA"
        
        self.parent.bind('s',self.correctBind)
        self.parent.bind('d',self.falseBind)
        self.parent.bind('f',self.reviewBind)
        self.parent.bind('g',self.skipBind)
        
        self.popup = tk.Toplevel()
        self.wfs = WaveformWindow(self.popup, self)
        self.wfs.pack(side="top", fill="both", expand=True)
                
        self.popup.protocol("WM_DELETE_WINDOW", self.wfs.on_closing)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        self.closed = 0
        
        self.map_popup = tk.Toplevel()
        self.map = MapWindow(self.map_popup)
        self.map.pack(side="top", fill="both", expand=True)
        
        self.map_popup.protocol("WM_DELETE_WINDOW", self.map.on_closing)
        
        self.winfo_toplevel().title("Pick Viewer")
        
        #Members#
        self.pick_df = pd.DataFrame()
        self.orid_df = pd.DataFrame()
        self.orig_locs = {'lat':[],'lon':[]}
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
        self.wf_B = self.Button('view waveform', f=self.showWindow)
        
        self.correct_B = self.Button('correct',f=partial(self.scrollDown,'correct'),row=2, column=3)
        self.false_B = self.Button('false', f=partial(self.scrollDown,'false'),row=3,column=3)
        self.review_B = self.Button('review', f=partial(self.scrollDown,'review'),row=4,column=3)
        self.prev_B = self.Button('prev',f=self.scrollUp,row=2,column=0)
        self.skip_B = self.Button('skip',f=partial(self.scrollDown,'skip'),row=5,column=3)
        
        self.Label("picks csv",row=2,column=1)
        self.csv_E = self.Entry(row=3,column=1,width=50, pady=10)
        self.FB = self.Button("Choose File",f=self.FileWindow, row=3,column=2)
        self.read_B = self.Button("read", f=self.loadDF, row=4)
        
        self.time_L = self.Label(self.p_date, row=5)
        self.id_L = self.Label(self.p_id, row=6)
        self.N_L = self.Label("%s/%s" % (str(self.N),str(self.Npicks)), row=5, column=0)
        self.status_L = self.Label("Status: %s" % "None", row=5,column=2)

        
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
        
        for event in self.evList:
            self.orig_locs['lat'].append(event.lat)
            self.orig_locs['lon'].append(event.lon)
        self.orig_locs = pd.DataFrame.from_dict(self.orig_locs)
        
        self.Npicks = len(self.orid_list)
        self.N = 0
        
        self.updateInfo()
        self.showWindow()
    
    def FileWindow(self, event=None):
        self.csv_E.delete(0,'end')
        filename = filedialog.askopenfilename()
        self.csv_E.insert(0,filename)
        

            
    def updateInfo(self):
        self.time_L.config(text=self.evList[self.N].time)
        self.id_L.config(text=self.evList[self.N].orid)
        self.N_L.config(text="%s/%s" % (str(self.N),str(self.Npicks)))
        self.status_L.config(text="Status: %s" % self.evList[self.N].status)
        self.current_event_status = self.evList[self.N].status

    
    def scrollUp(self):
        self.N = (self.N - 1)%self.Npicks
        self.updateInfo()
        self.updateWindow()
    
    def scrollDown(self, status):
        if status != 'skip':
            self.evList[self.N].status = status
        self.N = (self.N + 1)%self.Npicks
        self.updateInfo()
        
        self.updateWindow()
        
    def saveOut(self):
        for index,i in enumerate(self.orid_list):
            self.orid_checklist.iloc[index] = i, self.evList[self.evList.index(i)].status
        
        self.orid_checklist.to_csv('%s-out.csv' % self.csv_E.get())

    ###BINDINGS
    def correctBind(self, _event=None):
        self.scrollDown('correct')
    def falseBind(self, _event=None):
        self.scrollDown('false')
    def reviewBind(self, _event=None):
        self.scrollDown('review')
    def skipBind(self, _event=None):
        self.scrollDown('skip')
    ###
    
        
    def Debug(self):
        print(self.pick_df)
        
    def showWindow(self):

        self.map_popup.update()
        self.map_popup.deiconify()
        self.map.plot(self.orig_locs, self.evList[self.N])
        
        self.popup.update()
        self.popup.deiconify()
        self.wfs.plot(self.evList[self.N].evInfo, self.path)
        
    def updateWindow(self):
        self.map.plot(self.orig_locs, self.evList[self.N])
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