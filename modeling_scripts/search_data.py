#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 21:19:16 2019

@author: chrisolen
"""

import pandas as pd
import numpy as np

import os

import sys
sys.path.append("/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/audio_generation")
from data_cleaning_scripts import data_cleaning_scripts as dcs


def search_params():
    ans = {}
    length = len(ans)
    
    # Time Signature
    while len(ans) == length:
        time_signature = input("Indicate your preferred time signature [3/4, 4/4, 5/4, 6/8 or no preference]: ")
        
        if time_signature != "3/4" and time_signature != "4/4" and time_signature != "5/4" and \
        time_signature != "5/4" and time_signature != "6/8" and time_signature != "N/A":
            print("Enter a valid input: [3/4, 4/4, 5/4, 6/8 or no preference]: ")
        else:
            ans["time_signature"]=time_signature
    
    return ans
            

class track_search():
    
    """Default Track Attributes"""
    _defaults = dict(artist=None, 
                 song_title = None,
                 time_signature = "4/4", # most common
                 tempo = None,
                 energy = None,
                 loudness = None,
                 speechiness = None,
                 acousticness = None,
                 instrumentalness = None,
                 genre = [],
                 instruments = 7, # most common
                 percussion = 0,
                 time_signature_changes = 'no',
                 key_signature = 'G')
    
    
    def __init__(self, **sparams):
        
        """Determine any differences between default params and sparams"""
        
        self.data_dir = dcs.data_manip().data_dir
        self.scripts_dir = dcs.data_manip().scrips_dir
        
        new_vals = {i:j for (i,j) in sparams.items() if sparams[i] != track_search._defaults[i]}
        if new_vals != {}:
            self.update(new_vals)
    
    def update(self, new_vals):
        
        """If differences exist in __init__, we make changes to
        default params"""
        
        for i in new_vals:
            track_search._defaults[i] = new_vals[i]
            
    def query(self):
        
        track_metadata = pd.read_csv(self.script_dir + 
                                     "data_cleaning_scripts/" 
                                     + "track_metadata_final.csv")
        
        
        
