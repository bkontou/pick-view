#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 10:44:52 2019
@author: Byron Kontou
"""
import obspy as op
import numpy as np
import os

class Stream(op.Stream):
    def __init__(self, traces=None, **kwargs):
        """
        Rework of Stream from S-SNAP
        
        
        Stream inherits everything from obspy.Stream so it is in itself an obspy stream object
        
        Giving it the required information, it will then build a stream of all specified channels in sta_cat
        
        Expected Kwargs
        -------------
        [starttime,
         sta_cat,
         area_id
         path]
        
        Optional Kwargs
        ---------------
        sr
        
        Parameters
        ----------
        starttime: Start time of processing before overlap; UTCDateTime object
        
        sta_cat: Station catalogue dataframe containing all station and location information, build in run_master
        
        area_id: Unique id for area, corresponding to that in sta_cat
        
        path: Path to waveform database. Should have folders inside it in the form of path/YYYY/MM/DD/<filename>.mseed
        
        sr: samplling rate
        
        TO FIX
        ------
        For some reason the first argument given to Stream when constructed is left out of args
        and op.Stream.select constructs a new stream, so I have put all the arguments into a **kwargs
        """
        
        if 'sr' not in kwargs:
            self.sr = 100
        else:
            self.sr = kwargs['sr']
    
        op.Stream.__init__(self)
        
        if 'path' in kwargs:
            self.path = kwargs['path']
        
            if kwargs['path'].endswith('/'):
                self.path += str(kwargs['starttime'].year) + '/'
            else:
                self.path += '/' + str(kwargs['starttime'].year) + '/'
        
        if 'starttime' in kwargs:
            self.starttime = kwargs['starttime']
        
        if 'endtime' in kwargs:
            self.endtime = kwargs['endtime']
        
        if 'starttime' in kwargs and 'endtime' in kwargs:
            self.seconds = int(self.endtime - self.starttime)

        if 'origDF' in kwargs:
            self.origDF = kwargs['origDF']
            
        if 'cha' in kwargs:
            self.cha = kwargs['cha']
            
    def __contains__(self, i):
        """
        Magic method for 'in'
        Returns true if trace id is in stream
        
        Parameters
        ----------
        i: Trace id to search for in the form of 'NETWORK.STATION..CHANNEL'
        
        Returns
        -------
        True if trace id is in stream
        False otherwise
        """
        for t in self:
            if t.id == i:
                return True
        return False

        return t
    
    def _find_file(self, files, s,c,n=None):
        """
        Finds the file containing station, network, and optional channel name
        
        Parameters
        ----------
        files: list of file names
        
        s: station name
        
        n: network name
        
        c: channel name
        
        Returns
        -------
        If file is found: returns file name
        else: returns 0
        """
        for f in files:
            if n == None:
                if str(s) in f and str(c) in f:
                    return f
            else:
                if str(s) in f and str(n) in f and str(c) in f:
                    return f
        return 0
    
    def _get_trace(self, file, n, c, s, starttime=None, endtime=None):
        """
        Gets trace from a waveform file from specified start to end time
        
        Parameters
        ----------
        file: name of waveform file
        
        s: station name
        
        n: network name
        
        c: channel name
        
        starttime: UTCDateTime object of starttime
        
        endtime: UTCDateTime object of endtime
        
        Returns
        -------
        If waveform can be found, returns waveform
        else, will return a zeroed waveform
        """
        try:
            return op.read(file, starttime=self.starttime, endtime=self.endtime)
        except:
            s = str(s)
            n = str(n)
            c = str(c)
            print("Warning: file %s %s %s either missing or corrupt. Zeroing waveform." % (s,n,c))
            tid = n+"."+s+".."+c
            t = op.Trace()
            t.id = tid
            t.stats.starttime = starttime
            t.stats.sampling_rate = self.sr
            t.stats.npts = self.seconds*self.sr + 1
            t.data = np.zeros(self.seconds*self.sr + 1, dtype=np.int32)

            return t
              
        
        
    
    def fill_stream(self):
        """
        Fill stream object with waveforms from database specified in sta_cat dataframe
        """
        for index, row in self.origDF.iterrows():
            s = row['sta']
            n = row['net']
            c = self.cha
            month = str(self.starttime.month).zfill(2)
            day = str(self.starttime.day).zfill(2)
            
    #        print(starttime.year,starttime.month,starttime.day,starttime.hour)
            file = ""
            files = os.listdir(self.path + month + '/' + day + '/')
    
            if self.starttime.day == 1 and self.starttime.month == 1 and self.starttime.hour == 0:
                #print("first hour of the year")
                file = self.path + month + '/' + day + '/' + str(self._find_file(files,s,n,c))
                
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
            
            elif self.starttime.month == 12 and (self.starttime + 3600).month == 1:
                #print("last hour of the year")
                file = self.path + month + '/' + day + '/' + str(self._find_file(files,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
            elif (self.starttime + 3600).month > self.starttime.month:
                #print("last hour of the month")
                file = self.path + month + '/' + day + '/' + str(self._find_file(files,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
    
                monthnext = str((self.starttime + 3600).month).zfill(2)
                dayprev = "01"
                
                filesprev = os.listdir(self.path + monthnext + '/' + dayprev + '/')
                
                file = self.path + monthnext + '/' + dayprev + '/' + str(self._find_file(filesprev,s,n,c))
                
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
            elif int(self.starttime.hour) == 0:
                #print("first hour of day")
                file = self.path + month + '/' + day + '/' + str(self._find_file(files,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
    
    
                dayprev = str((self.starttime - 3600).day).zfill(2)
                monthprev = str((self.starttime - 3600).month).zfill(2)
                
                filesprev = os.listdir(self.path + monthprev + '/' + dayprev + '/')
                
                file = self.path + monthprev + '/' + dayprev + '/' + str(self._find_file(filesprev,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
    
            elif int(self.starttime.hour) == 23:
                #print("last hour of day")
                file = self.path + month + '/' + day + '/' + str(self._find_file(files,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
    
                daynext = str((self.starttime + 3600).day).zfill(2)
                filesprev = os.listdir(self.path + month + '/' + daynext + '/')
                
                file = self.path + month + '/' + daynext + '/' + str(self._find_file(filesprev,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)
            else:
                
                file = self.path + month + '/' + day + '/' + str(self._find_file(files,s,n,c))
                        
                self += self._get_trace(file, s, n, c, starttime=self.starttime, endtime=self.endtime)              

          
    def fix_cut(self):
        """
        Checks to see if any trace is cut into multiple smaller traces based off their unique IDs
        
        If there are multiple traces with the same ID, they will be added together
        Any missing data between cut traces will be filled with the linear interpolation between the
        start and end points of each trace
        """
        toappend = []
        newwf = self.copy()
        i = 0
        for it1, trace1 in enumerate(self):
            item = []
            idoi = trace1.id
            for it2, trace2 in enumerate(newwf):
                if trace1.id == trace2.id:
                    item.append(it2)
            for tr in newwf.select(id=idoi):
                tr.id = 'NA.NA..NA'
            toappend.append(item)
    
        newwf = op.Stream()
        for item in toappend:
            newtrace = op.Trace()
            if len(item) > 1:
                newtrace = self[item[0]].__add__(self[item[1]],fill_value='interpolate')
                if len(item) > 2:
                    for i in range(2,len(item)):
                        newtrace += self[item[i]]
                newwf += newtrace
            elif len(item) > 0:
                newwf += self[item[0]]
    
        wf = newwf.copy()
        newwf = op.Stream()
        for t in wf:
            if t.stats.npts != (self.seconds*self.sr + 1):
                newst = t.stats.__deepcopy__()
                newst.npts = self.seconds*self.sr + 1
                newst.starttime = self.starttime
    
                st1 = t.stats.__deepcopy__()
                st1.starttime = self.starttime
                st1.npts = 1
    
                st2 = st1.__deepcopy__()
                st2.starttime = self.endtime
    
                t1 = op.Trace(data=np.ones(1,dtype=t.data.dtype),header=st1)
                t2 = op.Trace(data=np.ones(1,dtype=t.data.dtype),header=st2)
    
                newt = (t.__add__(t1,fill_value=0)).__add__(t2,fill_value=0)
    
                newwf += newt
            else:
                newwf += t   
                
        self.clear()
        self += newwf
        
    def remove_duplicates(self):
        """
        Remove duplicate traces from stream
        """
        
        new = Stream()
        
        for t in self:
            if t.id in new:
                pass
            else:
                new += t
        
        self.clear()
        self += new
        del new
    
    def build(self):
        """
        build is a method that puts all the necessary steps to build a stream into one function to call
        """
        self.fill_stream()
        self.fix_cut()
        self.remove_duplicates()
        self.filter('bandpass', freqmin=2, freqmax=20)
        return self