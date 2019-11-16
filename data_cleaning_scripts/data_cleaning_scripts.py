import pandas as pd
import numpy as np

import shutil
import os
import time
from tqdm import tqdm
from tqdm import tqdm_notebook as tqdm_notebook

import spotipy
import spotipy.util as util

from requests.exceptions import ConnectionError 
from requests.exceptions import HTTPError
from requests.exceptions import SSLError
from urllib3.exceptions import MaxRetryError

import pretty_midi
import mido

import os

"""Sequence of actions:
    1. data_manip.download() to download requisite files
    2. data_manip.organize_files() to organize them and create metadata file
    3. spotify.call_loop() to use use existing track metadata to gather additional spotify metadata
    4. use_prettymidi.iter_through_midis() use prettymidi package to gather additional metadata"""

class data_manip(object):
    
    def __init__(self, 
             data_dir = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/audio_generation/data/",
             scripts_dir = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/audio_generation/NADE_music_generation/"):
        
        self.data_dir = data_dir
        self.scripts_dir = scripts_dir
        
    def download(self,
                 songlist = "http://millionsongdataset.com/sites/default/files/AdditionalFiles/unique_tracks.txt",
                 midifiles = "http://hog.ee.columbia.edu/craffel/lmd/lmd_matched.tar.gz"):
        
        #Download songlist text file
        os.system("curl '{}' -o {}".format(songlist, self.data_dir + "songlist_with_mbid.txt"))
        
        os.system("curl '{}' -o {}".format(midifiles, self.data_dir + "lmd_matched"))

        
    def organize_files(self):
        
        destination = self.data_dir + "midi_files/", 
        source = self.data_dir + "lmd_matched/"
        
        """Iterating thorugh the original file structure"""
        
        level_1 = os.listdir(source)
        for i in range(len(level_1)):
            if level_1[i] != ".DS_Store":
                level_2 = os.listdir(source+level_1[i]+"/")
                for j in range(len(level_2)):
                    if level_2[j] != ".DS_Store":
                        level_3 = os.listdir(source+level_1[i]+"/"+level_2[j]+"/")
                        for k in range(len(level_3)):
                            if level_3[k] != ".DS_Store":
                                level_4 = os.listdir(source+level_1[i]+"/"+level_2[j]+"/"+level_3[k]+"/")
                                for f in range(len(level_4)):
                                    if level_4[f] != ".DS_Store":
                                        shutil.move(source+level_1[i]+"/"+level_2[j]+"/"+level_3[k]+"/"+level_4[f],destination)
        
        """Create Metadata Table"""
                               
        # Read in textfile of 'Million Song Dataset' names:
        file = open(self.data_dir+"songlist_with_mbid.txt", 'r')
        lines = np.array(file.readlines())
        
        # Remove newline markers:
        cleaned_lines = [lines[i].replace("\n","") for i in range(len(lines))]
        
        # Split along "<SEP>"
        split_lines = [cleaned_lines[i].split("<SEP>") for i in range(len(cleaned_lines))] 
        
        # Merge into dataframe:
        tracks = pd.DataFrame.from_records(split_lines)
        tracks.rename(columns={0:"track_id",1:"mb_id",2:"artist",3:"song_title"},inplace=True)
        
        # Removing 'feat.' from the artists field:
        cleaned_artist = [tracks['artist'].iloc[i] if 'Feat.' not in tracks['artist'].iloc[i] else tracks['artist'].iloc[i].replace(tracks['artist'].iloc[i],tracks['artist'].iloc[i][tracks['artist'].iloc[i].find('Feat.'):][6:]) for i in range(len(tracks))]
        cleaned_artist_2 = [cleaned_artist[i] if 'feat.' not in cleaned_artist[i] else cleaned_artist[i].replace(cleaned_artist[i],cleaned_artist[i][cleaned_artist[i].find('feat.'):][6:]) for i in range(len(cleaned_artist))]
        tracks['artist'] = cleaned_artist_2
                                        
        # Retaining only records for which midi files exist
        unique_tracks = os.listdir(self.data_dir+'midi_files')
        tracks = tracks[tracks['track_id'].isin(unique_tracks)]
        
        # Write to disk: 
        tracks.to_csv(self.scripts_dir+"data_cleaning_scripts/track_metadata.txt")


class spotify(object):
    
    """Initialize w/ Default API Creds"""
    
    def __init__(self,
                 my_username="chrisolen",
                 chosen_scope='user-library-read',
                 my_client_id='###########',
                 my_client_secret='###########',
                 my_redirect_uri='https://grahamschool.uchicago.edu/academic-programs/masters-degrees/analytics'):
        
        self.my_username = my_username
        self.chosen_scope = chosen_scope
        self.my_client_id = my_client_id
        self.my_client_secret = my_client_secret
        self.my_redirect_uri = my_redirect_uri
        
    def auth_spotify(self):
       
        """Authenticate Connection"""
        
        token = util.prompt_for_user_token(username=self.my_username,
                                       scope=self.chosen_scope,
                                       client_id=self.my_client_id,
                                       client_secret=self.my_client_secret,
                                       redirect_uri=self.my_redirect_uri)
        sp = spotipy.Spotify(auth=token, requests_timeout=180)
        
        return sp
    
    def hit_spotify(self,
                    track_name, 
                    artist_name):
        
        """One round of hitting API with rate-limit contingencies"""
    
        sp = ''
        while sp == '':
            try:
                sp = self.auth_spotify()
            
            except (spotipy.client.SpotifyException, ConnectionError, MaxRetryError, 
                    TimeoutError, SSLError, HTTPError):
                tqdm.write("Going to sleep for 1 minute - Errored out on initial connect attempt")
                time.sleep(60)
        
        track_result = ''
        features = ''
        while track_result == '' and features == '':
            try:
                track_result = sp.search(q=track_name+" "+artist_name,type='track')
                track_id = track_result['tracks']['items'][0]['id']
                artist_id = track_result['tracks']['items'][0]['artists'][0]['id']
                features = sp.audio_features(track_id)
                time_sig = features[0]['time_signature'] 
                tempo = features[0]['tempo'] 
                energy = features[0]['energy'] 
                loudness = features[0]['loudness'] 
                speechiness = features[0]['speechiness'] 
                acousticness = features[0]['acousticness']
                instrumentalness = features[0]['instrumentalness'] 
                genre = sp.artists([artist_id])['artists'][0]['genres']
                result = np.array([track_id, artist_id, time_sig, tempo, energy, 
                                   loudness, speechiness, acousticness, 
                                   instrumentalness, genre])
                
                return result
            
            except (IndexError, TypeError): # Return NoneType when there are no results
                
                pass
            
            except (spotipy.client.SpotifyException, ConnectionError, 
                    MaxRetryError, TimeoutError, SSLError, HTTPError):
                tqdm.write("Going to sleep for 1 minute - Errored out on call")
                time.sleep(60)
                sp = self.auth_spotify() # Reauthenticate when the token expires
                
                continue
            
        def call_loop(self):
            
            """Looping through track metadata to call API, appending results to existing metadata"""
            
            ### The loop ###
            # Open existing metadata for loop iterable
            tracks = open(data_manip().scripts_dir+"data_cleaning_scripts/track_metadata.txt", 'r') 
            
            for i in tqdm_notebook(range(26585,len(tracks)), mininterval = 5.0, leave = False):
                result_array = self.hit_spotify(tracks.iloc[i]['song_title'], 
                                           tracks.iloc[i]['artist'])
                
                # Append if we have results
                try:
                    with open(data_manip().scripts_dir+
                              "data_cleaning_scripts/track_metadata.txt","ab") as textfile: 
                        np.savetxt(textfile,result_array.reshape(1, result_array.shape[0]), fmt="%s", delimiter=' | ')
                
                # Append NaN if we don't
                except AttributeError: 
                    with open(data_manip().scripts_dir+
                              "data_cleaning_scripts/track_metadata.txt","ab") as textfile: 
                        np.savetxt(textfile,np.array([np.NaN]), fmt="%s", delimiter=' | ')
            
            ### Cleaning up result of loop ###
            # Bring resulting textfile back into memory
            textfile = open(data_manip().scripts_dir+"data_cleaning_scripts/track_metadata.txt", 'r')
            track_features = np.array(textfile.readlines())
            
            # Remove newline markers:
            cleaned_features = [track_features[i].replace("\n","") for i in range(len(track_features))]
            
            # Split along " | "
            split_features = [cleaned_features[i].split(" | ") for i in range(len(cleaned_features))] 
            
            # Make the 'nan' lists have the same dimensions as the others:

            indexes = [i for i,x in enumerate(split_features) if x[0] == 'nan']
            extended = ['nan','nan','nan','nan','nan','nan','nan','nan','nan',['nan']]
            
            for i in range(len(indexes)):
                split_features[indexes[i]] = extended
                
            # Throwing the spotify features in a dataframe:
            spotify_features = pd.DataFrame(split_features, 
                                            columns = 
                                            ['sp_track_id', 'sp_artist_id', 
                                             'time_sig', 'tempo', 'energy', 
                                                             'loudness', 
                                                             'speechiness', 
                                                             'acousticness', 
                                                             'instrumentalness', 
                                                             'genre'])
    
            ### Merging the two frames ###
            # Reseting index of track dataframe to match up with features dataframe:
            tracks.reset_index(inplace= True)
            tracks.drop(['index'], axis = 1, inplace = True)
            
            # Merging two dateframes:
            track_metadata = tracks.merge(spotify_features, left_on=tracks.index, 
                                          right_on=spotify_features.index)
            track_metadata.drop(['key_0'], axis=1, inplace=True)
            
            # Write resulting df to csv:
            track_metadata.to_csv(data_manip().scripts_dir+
                                  "data_cleaning_scripts/track_metadata.csv")


# # Gathering Additional Metadata from Pretty Midi

class use_prettymidi(object):
    
    def __init__(self):
        
        """Read in track_metadata as class attribute"""
        
        self.track_metadata = pd.read_csv(data_manip().scripts_dir+
                                     "data_cleaning_scripts/track_metadata.csv")
        self.track_metadata.drop(["Unnamed: 0"], axis = 1, inplace = True)
        self.track_metadata = self.track_metadata.reindex(columns = self.track_metadata.columns.tolist() + 
                                                ["instruments","percussion",
                                                 "time_signature",
                                                 "time_signature_changes",
                                                 "key_signature","mid_id"])
        self.track_metadata.set_index('track_id', inplace=True)
        
        
    def meta_from_prettymidi(self,midi_data):
       
        """Function to extract time signature, key signature, 
        and instrumentation from pretty midi metadata:"""
        
        instruments = {}
        percussion = {}
        time_signature = ""
        time_signature_changes = ""
        key_signature = []
        
        try: 
        
            for i in range(len(midi_data.instruments)): # pulling out instruments and percussion into sep dicts
                if not midi_data.instruments[i].is_drum:
                    instruments.update({midi_data.instruments[i].program:(midi_data.instruments[i].name).rstrip()})
                else:
                    percussion.update({midi_data.instruments[i].program:(midi_data.instruments[i].name).rstrip()})

                if len(midi_data.time_signature_changes) > 1: # pulling out time sigs if there are changes
                    time_signature_changes = "yes"
                    res = ["{}/{}".format(midi_data.time_signature_changes[i].numerator,midi_data.time_signature_changes[i].denominator) for i in range(len(midi_data.time_signature_changes))]
                    time_signature = res
                    
                elif len(midi_data.time_signature_changes) == 1: # pulling out time sigs if there no changes
                    time_signature_changes = "no"
                    res = "{}/{}".format(midi_data.time_signature_changes[0].numerator,midi_data.time_signature_changes[0].denominator)
                    time_signature = res
        
                else:
                    time_signature_changes = np.NaN
                    time_signature = np.NaN
            
        except:
            pass
        
    
        keys = midi_data.get_pitch_class_histogram().argsort()[-2:][::-1]
        key_ref = ["C","C*","D","D*","E","F","F*","G","G*","A","A*","B"]    
        key_signature = [key_ref[i] for i in keys]

        frame = [instruments,percussion,time_signature,time_signature_changes,key_signature]

        return frame
    
    def iter_through_midis(self):
        
        """Iterating through file structure to apply 
        meta_from_prettymidi and concat to track_metadata"""
        
        source = data_manip().data_dir+"midi_files/"
        level_1 = os.listdir(source)
        
        for i in range(len(level_1)):
            print(i,level_1[i])
            try: 
        
                # Some of the corrupted files error out despite measures taken below
                # Namely: TRMPFNL128F427F0BF, TRNCSKU128F4265639, TRQODEY12903CF7594
    
                if level_1[i] != ".DS_Store":
                    level_2 = os.listdir(source + level_1[i]+ "/")
                    if level_2[0] == ".DS_Store":
                        dest = source + level_1[i] + "/" + level_2[1]
                        try:
                        
                            # In certain cases, we can clip midi files to be able to read them in
                    
                            midi_data = pretty_midi.PrettyMIDI(dest)
                            output = self.meta_from_prettymidi(midi_data)    
                            self.track_metadata.loc[level_1[i],["instruments",
                                                    "percussion","time_signature",
                                       "time_signature_changes","key_signature"]] = output   
                            self.track_metadata.loc[level_1[i],'mid_id'] = level_2[1]

                        except(OSError, KeyError):
                            mido.MidiFile(dest, clip = True).save(source + 
                                         level_1[i] + "/" + "clipped")
                            midi_data = pretty_midi.PrettyMIDI(source + 
                                                               level_1[i] + "/" + "clipped")
                            output = self.meta_from_prettymidi(midi_data)    
                            self.track_metadata.loc[level_1[i],["instruments",
                                                    "percussion","time_signature",
                                       "time_signature_changes","key_signature"]] = output   
                            self.track_metadata.loc[level_1[i],'mid_id'] = "clipped"
                    
                            # In other cases, clipping does not work    
            
                        except mido.midifiles.meta.KeySignatureError as k:
                            self.track_metadata.loc[level_1[i],'mid_id'] = "{}".format(str(k))
                            print(str(k))
                
                        except ValueError as v:
                            self.track_metadata.loc[level_1[i],'mid_id'] = "{}".format(str(v))
                            print(str(v))
                
                        except EOFError as e:
                            self.track_metadata.loc[level_1[i],'mid_id'] = "{}".format(str(e))
                            print(str(e))
                    
                    else:
                        dest = source + level_1[i] + "/" + level_2[0]
                        try:
                            midi_data = pretty_midi.PrettyMIDI(dest)
                            output = self.meta_from_prettymidi(midi_data)    
                            self.track_metadata.loc[level_1[i],["instruments",
                                                    "percussion","time_signature",
                                       "time_signature_changes","key_signature"]] = output   
                            self.track_metadata.loc[level_1[i],'mid_id'] = level_2[0] 
                
                        except(OSError, KeyError):
                            mido.MidiFile(dest, clip = True).save(source + 
                                         level_1[i] + "/" + "clipped")
                            midi_data = pretty_midi.PrettyMIDI(source + 
                                                               level_1[i] + "/" + "clipped")
                            output = self.meta_from_prettymidi(midi_data)    
                            self.track_metadata.loc[level_1[i],["instruments",
                                                    "percussion","time_signature",
                                       "time_signature_changes","key_signature"]] = output   
                            self.track_metadata.loc[level_1[i],'mid_id'] = "clipped"
                
                        except mido.midifiles.meta.KeySignatureError as k:
                            self.track_metadata.loc[level_1[i],'mid_id'] = "{}".format(str(k))
                            print(str(k))
            
                        except ValueError as v:
                            self.track_metadata.loc[level_1[i],'mid_id'] = "{}".format(str(v))
                            print(str(v))
                
                        except EOFError as e:
                            self.track_metadata.loc[level_1[i],'mid_id'] = "{}".format(str(e))
                            print(str(e))
            
            except:
                self.track_metadata.loc[level_1[i],'mid_id'] = "unknown error"
                pass

        # Write final to csv:
        self.track_metadata.to_csv(data_manip().scripts_dir+"data_cleaning_scripts/track_metadata_final.csv")






