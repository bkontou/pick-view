# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:10:06 2019

@author: bkontou
"""
from main import *
from stream import Stream

class WaveformWindow(MainApplication):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent=None, *args, **kwargs)
        self.parent = parent
        
        self.stream = op.Stream()
        
        self.widget = None
        self.toolbar = None
      
    def readWf(self, path, start, end, sta, chan):
        self.stream = Stream(path=path, starttime=start, endtime=end, sta=sta, cha=chan).build()
    
    def plot(self):
        
        if self.widget:
            self.widget.destroy()
        
        if self.toolbar:
            self.toolbar.destroy()
        
        
        t = op.Trace()
        t.data = np.random.rand(500)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        a = self.fig.add_subplot(111)
        a.plot(t.data, label="AAAA")
        a.set_ylabel("AAAA")
        a.set_title("AAAAAAA")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill=tk.BOTH)
        
        self.canvas.draw()
        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)        
    
    def on_closing(self):
        self.parent.withdraw()
