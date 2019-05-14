# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:10:06 2019

@author: bkontou
"""
from main import *
from stream import Stream

class WaveformWindow(MainApplication):
    def __init__(self, parent, master, *args, **kwargs):
        tk.Frame.__init__(self, parent=None, *args, **kwargs)
        self.parent = parent
        self.master = master
        print(self.master.test)
        
        self.streamV = op.Stream()
        self.streamH = op.Stream()
        
        self.widget = None
        self.toolbar = None
        
        self.parent.bind('s',self.master.correctBind)
        self.parent.bind('d',self.master.falseBind)
        self.parent.bind('f',self.master.reviewBind)
        self.parent.bind('g',self.master.skipBind)
        
      
    def readWf(self, path, start, end, origDF):
        self.streamV = Stream(path=path, starttime=start, endtime=end, origDF=origDF, cha='HHZ').build()
        self.streamH = Stream(path=path, starttime=start, endtime=end, origDF=origDF, cha='HHE').build()
    
    def plot(self, event):
        
        if self.widget:
            self.widget.destroy()
        
        if self.toolbar:
            self.toolbar.destroy()
        

        cut_start = 10 #time in seconds to cut from start
        cut_end = 10   #same thing but for the end
        
        self.canvas = FigureCanvasTkAgg(event.fig, master=self.parent)  # A tk.DrawingArea.
        #self.canvas.flush_events()
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill=tk.BOTH)
        
        self.canvas.draw()
        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)        
    
    def on_closing(self):
        self.parent.withdraw()


class MapWindow(MainApplication):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent=None, *args, **kwargs)
        self.parent = parent
        
        self.widget = None
        self.toolbar = None
    
    def plot(self, origins, current):
        if self.widget:
            self.widget.destroy()
        
        if self.toolbar:
            self.toolbar.destroy()
        
        self.fig = Figure(figsize=(6,6))
        self.a = self.fig.add_subplot(111)
        
        for ev in origins:
            if ev.status == 'unassigned':
                self.a.scatter(ev.lat,ev.lon, c='turquoise')
            if ev.status == 'correct':
                self.a.scatter(ev.lat,ev.lon, c='green')
            if ev.status == 'review':
                self.a.scatter(ev.lat,ev.lon, c='orange', alpha=0.5)
            if ev.status == 'false':
                pass
                #self.a.scatter(ev.lat,ev.lon, c='black')
            
        
        self.a.scatter(current.lat,current.lon, facecolors='none', edgecolors='r', s=80)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)  # A tk.DrawingArea.
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill=tk.BOTH)
        
        self.canvas.draw()
        
        
    def on_closing(self):
        self.parent.withdraw()
        
class WarningWindow(MainApplication):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent=None, *args, **kwargs)
        self.parent = parent
        
        self.label = self.Label("Loading waveforms")
        
class Test(MainApplication):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent=None, *args, **kwargs)
        self.parent = parent
        
        self.widget = None
        self.toolbar = None
        
        self.ani = None
    
    def plot(self):
        
        print("OOOOO")