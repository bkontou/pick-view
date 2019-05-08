#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 11:32:20 2019

@author: pgcseismolab
"""

class Event:
    def __init__(self, evInfo):
        self.evInfo = evInfo.sort_values('arrival_time')
        
        self.orid = evInfo.iloc[0].orid
        self.time = evInfo.iloc[0].datetime
        self.status = 'unassigned'
        
        self.lat = evInfo.iloc[0].lat
        self.lon = evInfo.iloc[0].lon
    
    def __eq__(self, orid):
        if self.orid == orid:
            return True
        else:
            return False
        
    