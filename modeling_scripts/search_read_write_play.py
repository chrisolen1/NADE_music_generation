#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import numpy as np

import os

import pypianoroll
import pretty_midi

import pygame

from matplotlib import pyplot as plt



data_dir = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/audio_generation/data/"
scripts_dir = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/audio_generation/NADE_music_generation/"


# # Read In Track Metadata

# Read in track metadata:

track_metadata = pd.read_csv(scripts_dir+"data_cleaning_scripts/track_metadata.csv",
                            index_col='Unnamed: 0')


track_metadata.head()
track_metadata.columns

track_metadata['loudness'].quantile(.01111111)



track_metadata.shape


# # Read in Midi Files


# Locate desired track_id from metadata:

track_id = track_metadata.iloc[800,0]



# Find the corresponding midi file:

midi_id = os.listdir(data_dir+"midi_files/"+ track_id)[0]



# Load in the full path:

mid = pypianoroll.Multitrack(data_dir+"midi_files/"+ track_id + "/" + midi_id)



# Is it binarized?

mid.is_binarized()



# Binarize:

mid.binarize()



# Store binarized int pianoroll as separate object:

roll = mid.get_stacked_pianoroll().astype(int)



roll.shape



# Multitrack object metadata:

instrumentation = [mid.tracks[i].program for i in range(len(mid.tracks))]

unique, counts = np.unique(mid.tempo, return_counts=True)
tempo = dict(zip(unique, counts))

beat_res = mid.beat_resolution # number of time steps per beat

active_length = mid.get_active_length() # number of time steps where there's some activity

pitch_range = mid.get_active_pitch_range()



# Pianoroll object metadata (for one voice):

empty_beat_rate = pypianoroll.metrics.empty_beat_rate(roll[:,:,0], beat_res) # Ratio of empty beats to the total number of beats

num_pitches_used = pypianoroll.metrics.n_pitches_used(roll[:,:,0])



# Write multitrack pianroll to a MIDI file:

mid.write(scripts_dir + "modeling_scripts/"+"test_midi")



mid


# # Pretty Midi


midi_data = pretty_midi.PrettyMIDI(data_dir+"midi_files/"+ track_id + "/" + midi_id)



midi_data.estimate_tempo()



help(midi_data)



midi_data.instruments



midi_data.key_signature_changes



midi_data.time_signature_changes



midi_data.get_beats()[0:5]



midi_data.get_chroma().shape



midi_data.get_piano_roll().shape



midi_data.estimate_beat_start()



midi_data.get_downbeats()[0:5]



midi_data.get_pitch_class_histogram()



midi_data.__dict__



midi_data.time_to_tick(time=1)



midi_data.get_piano_roll()[30:90,2000:2015]


# # Playing Midi File in Python


pygame.mixer.init()
pygame.mixer.music.load(data_dir+"midi_files/"+ track_id + "/" + midi_id)
pygame.mixer.music.play()



pygame.mixer.music.stop()


# # Plotting




