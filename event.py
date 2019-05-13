#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 11:32:20 2019

@author: pgcseismolab
"""
from stream import Stream
import obspy as op
from main import *

class Event:
    def __init__(self, evInfo):
        self.evInfo = evInfo.sort_values('arrival_time')
        
        self.orid = evInfo.iloc[0].orid
        
        self.cut_start = 10
        self.cut_end = 10 
        
        self.timemin = evInfo.datetime.apply(op.UTCDateTime).min()-self.cut_start
        self.timemax = evInfo.datetime.apply(op.UTCDateTime).max()+self.cut_end
        
        self.status = 'unassigned'
        
        self.lat = evInfo.iloc[0].lat
        self.lon = evInfo.iloc[0].lon
        
        self.streamV = Stream()
        self.streamH = Stream()
        
        self.fig = Figure(figsize=(16, 16), dpi=100)
        
    def loadFig(self):
        a = self.fig.add_subplot(len(self.streamV),2,1)
        n = 1
        for tv, th in zip(self.streamV, self.streamH):
            tv.data = tv.data[self.cut_start*100:]
            tv.data = tv.data[:len(tv.data)-self.cut_end]
            
            th.data = th.data[self.cut_start*100:]
            th.data = th.data[:len(th.data)-self.cut_end]
            
            a = self.fig.add_subplot(len(self.streamH),2,2*n)
            a.plot(th, label=th.id)
            for index, row in self.evInfo.iterrows():
                if row['sta'] == th.stats.station:
                    cut_time = self.timemin
                    pick_loc = int((op.UTCDateTime(row['datetime']) - cut_time)*100)
                    #pick_loc = (op.UTCDateTime(row['datetime']) - start_time)*100
                    if row['phase'] == 'S':
                        a.axvline(x=pick_loc, c='black')
                        a.text(pick_loc+1,0, row['phase'], rotation=90)
            

            a = self.fig.add_subplot(len(self.streamV),2,2*n-1)
            a.plot(tv, label=tv.id)
            for index, row in self.evInfo.iterrows():
                if row['sta'] == tv.stats.station:
                    cut_time = self.timemin
                    pick_loc = int((op.UTCDateTime(row['datetime']) - cut_time)*100)
                    #pick_loc = (op.UTCDateTime(row['datetime']) - start_time)*100
                    if row['phase'] == 'P':
                        a.axvline(x=pick_loc, c='black')
                        a.text(pick_loc+1,0, row['phase'], rotation=90)
            
            n += 1

        self.fig.text(0,0,"ORID: %s" % self.evInfo.iloc[0].orid)
    
    def __eq__(self, orid):
        if self.orid == orid:
            return True
        else:
            return False
        
    