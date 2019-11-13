#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 21:19:16 2019

@author: chrisolen
"""

import pandas as pd
import numpy as np

import os

# raw input:

data_dir = "/Users/chrisolen/Documents/uchicago_courses/"\
"deep_learning_and_image_recognition/audio_generation/"\
"data/midi_files/"

scripts_dir = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/audio_generation/NADE_music_generation/"

track_metadata = pd.read_csv(scripts_dir+"data_cleaning_scripts/track_metadata.csv",
                            index_col='Unnamed: 0')

def search_params():
    ans = {}
    length = len(ans)
    # Time Signature
    while len(ans) == length:
        time_sig = input("Indicate your preferred time signature [3, 4, 5, or N/A]")
        if time_sig != "3" and time_sig != "4" and time_sig != "5" and time_sig != "N/A":
            print("fuck you!")
        else:
            ans["time_sig"]=time_sig
    return ans
            



class data_search(**sparams):
            
        """Default Attributes"""
        artist = None
        song_title = None
        time_sig = 4.0
        tempo = None
        energy = None
        loudness = None
        speechiness = None
        acousticness = None,
        instrumentalness = None
        genre = []
        

ans = {}
len(ans)

(['track_id', 'mb_id', 'artist', 'song_title', 'sp_track_id',
       'sp_artist_id', 'time_sig', 'tempo', 'energy', 'loudness',
       'speechiness', 'acousticness', 'instrumentalness', 'genre'],
      dtype='object')