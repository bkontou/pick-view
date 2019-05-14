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
import pickle

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from functools import partial

from windows import *
from stream import Stream
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
        
        self.test_popup = tk.Toplevel()
        self.test = Test(self.test_popup)
        self.test.pack(side="top", fill="both", expand=True)
        
        self.map_popup.protocol("WM_DELETE_WINDOW", self.map.on_closing)
        
        self.winfo_toplevel().title("Pick Viewer")
        
        #Members#
        self.pick_df = pd.DataFrame()
        self.orid_df = pd.DataFrame()
        self.orig_locs = {'lat':[],'lon':[]}
        self.orid_checklist = {'orid':[],'status':[]}
        
        self.orid_list = []
        self.Npicks = len(self.pick_df)
        self.N = 0
        self.group_N = 0
        self.pick_info = {}
        
        self.current_event_status = False
        
        self.evList = []
        
        ###CHANGE THIS###
        self.path = 'C:/Users/bkontou/Documents/archive'
        self.maxwf = 5
        
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
        self.FB = self.Button("Choose File",f=partial(self.FileWindow, self.csv_E), row=3,column=2)
        
        self.Label("load backup save",row=4,column=1)
        self.save_E = self.Entry(row=5, column=1, width=50)
        self.save_FB = self.Button("Choose File", f=partial(self.FileWindow,self.save_E),row=5,column=2)
        
        
        self.read_B = self.Button("read", f=self.load, row=6, pady=10)
        
        self.time_L = self.Label(self.p_date, row=7)
        self.id_L = self.Label(self.p_id, row=8)
        self.N_L = self.Label("%s/%s" % (str(self.N),str(self.Npicks)), row=7, column=0)
        self.status_L = self.Label("Status: %s" % "None", row=7,column=2)

        
        self.save_B = self.Button("Save", f=self.saveOut, row=9,column=0)
        #self.goodev_CB.configure(state='disable')
        
    def load(self):
        if self.save_E.get():
            self.loadSave()
        elif self.csv_E.get():
            self.loadDF()
        else:
            print("No file selected")
        
    def loadDF(self):
        self.pick_df = pd.read_csv(self.csv_E.get())
        self.pick_df = self.pick_df.sort_values('orid')
        self.orid_list = self.pick_df.orid.unique()
        
        #update eventlist
        for orid in self.orid_list:
            self.evList.append(Event(self.pick_df[self.pick_df.orid == orid]))
        
        
        self.Npicks = len(self.orid_list)
        self.N = 0
        
        self.updateWaveforms()
        
        self.updateInfo()
        self.showWindow()
        
    def loadSave(self):
        with open(self.save_E.get(),'rb') as f:
            info = pickle.load(f)
            
        self.evList = info['evList']
        self.N = info['N']
        self.Npicks = info['Npicks']
        self.group_N = info['group_N']
        
        self.updateWaveforms()
        
        self.updateInfo()
        self.updateWindow()
    
    def FileWindow(self, entry, event=None):
        entry.delete(0,'end')
        filename = filedialog.askopenfilename()
        entry.insert(0,filename)
        

    def updateWaveforms(self):
        
        self.loading = tk.Toplevel()
        self.loading_err = WarningWindow(self.loading)
        self.loading_err.pack(side="top", fill="both", expand=True)
        
        
        for event in self.evList:
            event.streamH = Stream()
            event.streamV = Stream()
        
        for ev in self.evList[self.group_N*self.maxwf:self.group_N*self.maxwf+self.maxwf]:
            
            cut_start = 10 #time in seconds to cut from start
            cut_end = 10   #same thing but for the end
            start_time = ev.timemin-cut_start
            end_time = ev.timemax+cut_end
            
            ev.streamH = Stream(path=self.path, starttime=start_time, endtime=end_time, origDF=ev.evInfo, cha='HHE').build()
            ev.streamV = Stream(path=self.path, starttime=start_time, endtime=end_time, origDF=ev.evInfo, cha='HHZ').build()
    
            ev.loadFig()


    def updateInfo(self):
        self.time_L.config(text=self.evList[self.N].timemin)
        self.id_L.config(text=self.evList[self.N].orid)
        self.N_L.config(text="%s/%s" % (str(self.N),str(self.Npicks)))
        self.status_L.config(text="Status: %s" % self.evList[self.N].status)
        self.current_event_status = self.evList[self.N].status

    
    def scrollUp(self):
        self.N = (self.N - 1)%self.Npicks
        
        if self.N%self.maxwf == 0 and self.N != 0:
            print("reading new waveforms")
            self.group_N -= 1
            self.updateWaveforms()
        
        self.updateInfo()
        self.updateWindow()
    
    def scrollDown(self, status):
        if status != 'skip':
            self.evList[self.N].status = status
        self.N = (self.N + 1)%self.Npicks
        
        if self.N%self.maxwf == 0 and self.N != 0:
            print("reading new waveforms")
            self.group_N += 1
            self.updateWaveforms()
        
        self.updateInfo()
        self.updateWindow()
        
    def saveOut(self, crash=False):
        for event in self.evList:
            self.orid_checklist['orid'].append(event.orid)
            self.orid_checklist['status'].append(event.status)
        
        self.orid_checklist = pd.DataFrame.from_dict(self.orid_checklist)
        
        if crash:
            self.orid_checklist.to_csv('backup.csv')
        else:
            self.orid_checklist.to_csv('%s-out.csv' % self.csv_E.get())
                    
    def saveState(self):
        stateDict = {'evList':self.evList,
                     'N':self.N,
                     'Npicks':self.Npicks,
                     'group_N':self.group_N}
        
        with open('./saves/%s.p' % 'backup','wb') as f:
            pickle.dump(stateDict, f)

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
        self.map.plot(self.evList, self.evList[self.N])
        
        self.popup.update()
        self.popup.deiconify()
        self.wfs.plot(self.evList[self.N])
        
        self.test_popup.update()
        self.test_popup.deiconify()
        self.test.plot()
        
    def updateWindow(self):
        self.map.plot(self.evList, self.evList[self.N])
        self.wfs.plot(self.evList[self.N])
        
    def on_close(self):
        self.closed = 1
        #self.quit()
        
if __name__ == '__main__':
    running = True
    root = tk.Tk()
    MA = MainWindow(root)
    MA.pack(side="top", fill="both", expand=True)
        
    while running:
        try:
            root.update()
            if MA.closed:
                MA.saveState()
                root.destroy()
                running = 0
        except:
            MA.saveState()
    
    
    #root.mainloop()