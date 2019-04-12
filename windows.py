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
        
        self.streamV = op.Stream()
        self.streamH = op.Stream()
        
        self.widget = None
        self.toolbar = None
      
    def readWf(self, path, start, end, origDF):
        self.streamV = Stream(path=path, starttime=start, endtime=end, origDF=origDF, cha='HHZ').build()
        self.streamH = Stream(path=path, starttime=start, endtime=end, origDF=origDF, cha='HHE').build()
    
    def plot(self, origDF, path):
        
        if self.widget:
            self.widget.destroy()
        
        if self.toolbar:
            self.toolbar.destroy()
        
        cut_start = 10 #time in seconds to cut from start
        cut_end = 10   #same thing but for the end
        start_time = op.UTCDateTime(origDF.datetime.apply(op.UTCDateTime).min())-cut_start-5
        end_time = op.UTCDateTime(origDF.datetime.apply(op.UTCDateTime).max())+cut_end+5
        
        self.readWf(path, start=start_time, end=end_time, origDF=origDF)
        
        self.fig = Figure(figsize=(16, 8), dpi=100)
        a = self.fig.add_subplot(len(self.streamV),2,1)
        n = 1
        for tv, th in zip(self.streamV, self.streamH):
            tv.data = tv.data[cut_start*100:]
            tv.data = tv.data[:len(tv.data)-cut_end]
            
            th.data = th.data[cut_start*100:]
            th.data = th.data[:len(th.data)-cut_end]
            
            a = self.fig.add_subplot(len(self.streamH),2,2*n)
            a.plot(th, label=th.id)
            for index, row in origDF.iterrows():
                if row['sta'] == th.stats.station:
                    cut_time = start_time + cut_start
                    pick_loc = int((op.UTCDateTime(row['datetime']) - cut_time)*100)
                    #pick_loc = (op.UTCDateTime(row['datetime']) - start_time)*100
                    if row['phase'] == 'S':
                        a.axvline(x=pick_loc, c='black')
                        a.text(pick_loc+1,0, row['phase'], rotation=90)
            

            a = self.fig.add_subplot(len(self.streamV),2,2*n-1)
            a.plot(tv, label=tv.id)
            for index, row in origDF.iterrows():
                if row['sta'] == tv.stats.station:
                    cut_time = start_time + cut_start
                    pick_loc = int((op.UTCDateTime(row['datetime']) - cut_time)*100)
                    #pick_loc = (op.UTCDateTime(row['datetime']) - start_time)*100
                    if row['phase'] == 'P':
                        a.axvline(x=pick_loc, c='black')
                        a.text(pick_loc+1,0, row['phase'], rotation=90)
            
            n += 1

        self.fig.text(0,0,"ORID: %s" % origDF.iloc[0].orid)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)  # A tk.DrawingArea.
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill=tk.BOTH)
        
        self.canvas.draw()
        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)        
    
    def on_closing(self):
        self.parent.withdraw()
