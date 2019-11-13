#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

"""
Created on Wed Nov  6 16:47:39 2019

@author: chrisolen
"""

"""Utilities for converting to pianorolls"""


import numpy as np
import pretty_midi
import pypianoroll
import tensorflow as tf

class PianorollEncoderDecoder():
    
    def __init__(self,
                 min_pitch=30,
                 max_pitch=90,
                 binarize=False):
        
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.binarize = binarize
        
    def get_pianoroll(self, data_dir):
        mid = pypianoroll.Multitrack(data_dir)
        if not mid.is_binarized() and binarize==True: # we we want note velocity info?
            mid.binarize()
        roll = mid.get_stacked_pianoroll().astype(int)
        return roll
    
    
data_dir = "/Users/chrisolen/Documents/uchicago_courses/"\
"deep_learning_and_image_recognition/audio_generation/"\
"data/midi_files/TRAAGCZ128F93210FD/"\
"ed659b5f46e1530fea93bc3b61ae4164.mid"
    
    
            
encdec = PianorollEncoderDecoder()

res = encdec.get_pianoroll(data_dir)


        
        
        
res.shape
    
    
    
    
        
        
    
    