#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 11:32:20 2019

@author: pgcseismolab
"""
from stream import Stream
import obspy as op

class Event:
    def __init__(self, evInfo):
        self.evInfo = evInfo.sort_values('arrival_time')
        
        self.orid = evInfo.iloc[0].orid
        
        self.timemin = evInfo.datetime.apply(op.UTCDateTime).min()-10
        self.timemax = evInfo.datetime.apply(op.UTCDateTime).max()+10
        
        self.status = 'unassigned'
        
        self.lat = evInfo.iloc[0].lat
        self.lon = evInfo.iloc[0].lon
        
        self.streamV = Stream()
        self.streamH = Stream()
    
    def __eq__(self, orid):
        if self.orid == orid:
            return True
        else:
            return False
        
    