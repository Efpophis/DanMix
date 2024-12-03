#!/usr/bin/env python

import FreeSimpleGUI as sg
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
import sys, glob

def build_layout(files):
    master_controls = [
                    [sg.Push(), sg.Text('11'), sg.Push()],
                    [sg.Text('Vol:'), sg.Slider((0,100), orientation='vertical', expand_y=True, default_value=75, enable_events=True, disable_number_display=True, key=f'Vol::master')],
                     #sg.Text('    '),
                    #sg.Slider((-100,100), orientation='vertical', expand_y=True, default_value=0, enable_events=True, disable_number_display=True, key=f'Pan::master'), sg.Button('Center', key='Ctr::master', button_color='green')],
                    [sg.Push(), sg.Text('0'), sg.Push()], #, sg.Text('      Pan')],
                    [sg.HorizontalSeparator(key='sep1')],
                    [sg.Push(), sg.Button('Mute All X', key='Mute::master'), sg.Push()], 
                    [sg.Push(), sg.Button('Pause All ||', key=f'Psr::master', disabled=True), sg.Push()],
                    [sg.Push(), sg.Button('Stop All []', key=f'Stop::master'), sg.Push()]

                       
                     ]
    
    dyn_layout = []    
    
    rgid=1
    for file in files:
        dyn_layout.append([sg.Text(f'File: {file}')])
        dyn_layout.append([sg.Push(), 
                           sg.Button("Play |>", key=f'Play::{file}'), sg.Button("Pause ||", key=f'Psr::{file}', disabled=True), 
                           sg.Button("Stop []", key=f'Stop::{file}'), 
                           sg.Radio('One shot',group_id=rgid, default=True, enable_events=True, key=f'Ones::{file}'),
                           sg.Radio('Loop', group_id=rgid, key=f'Loop::{file}', enable_events=True),
                          sg.Push()])
        dyn_layout.append([sg.Button('Mute X', key=f'Mute::{file}'), sg.Text('Volume: 0'), 
                      sg.Slider((0,100), orientation='horizontal', enable_events=True, default_value=75, disable_number_display=True,               key=f'Vol::{file}'),
                      sg.Text('11    |   Pan:   L'), 
                      sg.Slider((-100,100), orientation='horizontal', default_value=0, disable_number_display=True, enable_events=True,               key=f'Pan::{file}'),
                      sg.Text('R'), sg.Button('Center', key=f'Ctr::{file}', button_color='green')])
        dyn_layout.append([sg.HorizontalSeparator()])
        rgid += 1
    
    layout = [[sg.Frame('Master Controls',  master_controls, expand_y=True ), sg.Frame('Sounds', dyn_layout )]] 
    
    layout.append([sg.Push(), sg.Button('Exit'), sg.Push()])
    
    window = sg.Window("DanMix D&D Sound Board", layout)
    
    return layout, window

class AudioObject():
    def __init__(self, channel, sound, volume=75, pan=0, muted=False, playing=False, paused=False, looping=False):
        self.channel = channel
        self.sound = sound
        self.volume = volume
        self.pan = pan
        self.muted = muted
        self.playing = playing
        self.paused = paused
        self.looping = looping

class DanAudio():
    def __init__(self, audio_files):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(len(audio_files))
        self.m_audio_map = self.build_audio_map(audio_files)
        self.master_vol = 75
        self.master_pan = 0
        self.master_mute = False
        self.master_pause = False
        
    def calc_pan(self, vol_l, vol_r, pan):
        #print(f'Pan: vol_l={vol_l}, vol_r={vol_r}, pan={pan}')
        if pan == 0:
            #print('Pan: no-op')
            return vol_l, vol_r
        pan /= 100
        if pan > 0:
         #   print(f'new pan={pan}, vol_l={vol_l}, vol_r={vol_r*pan}')
            return vol_l - (vol_l * pan), vol_r
        if pan < 0:
          #  print(f'new pan={pan}, vol_l={vol_l * -pan}, vol_r={vol_r}')
            return vol_l, vol_r - (vol_r * -pan)
        
    def build_audio_map(self,audio_files):
        mymap = {}
        chid=0
        for file in audio_files:
            mymap[file] = AudioObject(channel=pygame.mixer.Channel(chid), sound=pygame.mixer.Sound(file))
            chid += 1
        return mymap
        
    def Pan(self, file, val):
        #print(f'PAN: {file} value == {val}\r\n')
        aud = self.m_audio_map[file]
        aud.pan = val
        if aud.muted == False:
            vol_l, vol_r = self.calc_pan(aud.volume/100, aud.volume/100, val )
            aud.channel.set_volume(vol_l, vol_r)

    def Vol(self, file, val):
        #print(f'VOL: {file} value = {val}\r\n')
        if file == 'master':
            if self.master_mute == False:
                self.master_vol = val
                for key, aud in self.m_audio_map.items():                
                    aud.sound.set_volume(val/100)
        else:
            aud = self.m_audio_map[file]
            aud.volume = val
            if aud.muted == False:
                vol_l, vol_r = self.calc_pan(val/100, val/100, aud.pan)
                aud.channel.set_volume(vol_l, vol_r)

    def Mute(self, file):
        # needs to toggle
        #print(f'Mute: {file}')
        if file == 'master':
            self.master_mute = not self.master_mute
            for key, aud in self.m_audio_map.items():
                if self.master_mute == False:
                    aud.sound.set_volume(self.master_vol)
                else:
                    aud.sound.set_volume(0)
        else:
            aud = self.m_audio_map[file]
            aud.muted = not aud.muted
            if aud.muted == False:
                vol_l, vol_r = self.calc_pan(aud.volume/100, aud.volume/100, aud.pan)
                aud.channel.set_volume(vol_l, vol_r)
            else:
                aud.channel.set_volume(0,0)
        

    def Play(self, file):
        #print(f'Play: {file}')
        if self.master_pause == False:
            aud = self.m_audio_map[file]
            nloops=0
            if aud.looping == True:
                nloops = -1
            if aud.muted == False:
                vol_l, vol_r = self.calc_pan(aud.volume/100, aud.volume/100, aud.pan)
                aud.channel.set_volume(vol_l, vol_r)            
            aud.channel.play(aud.sound, loops=nloops)
            aud.playing = True

    def Stop(self, file):    
        #print(f'Stop: {file}')
        aud = self.m_audio_map[file]
        aud.playing = False
        aud.channel.stop()

    def Pause(self, file, paused=None):
        # should also toggle
        #print(f'Pause/Resume: {file}')       
        aud = self.m_audio_map[file]
        if paused != None:
            aud.paused = paused
        else:
            aud.paused = not aud.paused
            
        if aud.paused == True:
            aud.channel.pause()                
        else:
            aud.channel.unpause()                

    def Loop(self, file):
        #print(f'Loop {file}')
        aud = self.m_audio_map[file]
        aud.looping = True

    def Clear_loop(self, file):
        #print(f'OneShot: {file}')
        aud = self.m_audio_map[file]
        aud.looping = False



def run_gui(layout, window, audio):
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        else:            
            if 'Pan::' in event:
                file = event[5:]
                val = values[event]                
                if val == 0:
                    window[f'Ctr::{file}'].update(button_color='green')
                else:
                    window[f'Ctr::{file}'].update(button_color=sg.theme_button_color())
                audio.Pan(file, val)
                
            if 'Ctr::' in event:
                # center the corresponding pan slider   
                file = event[5:]
         #      print(f'Center: {file}')
                window[f'Pan::{file}'].update(value=0)
                window[event].update(button_color='green')
                audio.Pan(file, 0)
                
            if 'Vol::' in event:
                file = event[5:]
                val = values[event]
                audio.Vol(file, val)
                
            if 'Mute::' in event:
                file = event[6:]                
                toggle_button_color(window[event])
                audio.Mute(file)
                
            if 'Play::' in event:
                file = event[6:]
                if audio.m_audio_map[file].playing == False:
                    toggle_button_color(window[event])
                    window[f'Psr::{file}'].update(disabled=False)
                    window['Psr::master'].update(disabled=False)
                    window[f'Ones::{file}'].update(disabled=True)
                    window[f'Loop::{file}'].update(disabled=True)
                    audio.Play(file)
                
            if 'Stop::' in event:
                file = event[6:]                
                if file != 'master':
                    window[f'Play::{file}'].update(button_color=sg.theme_button_color(), disabled=False)
                    window[f'Psr::{file}'].update(button_color=sg.theme_button_color(), disabled=True)
                    window[f'Ones::{file}'].update(disabled=False)
                    window[f'Loop::{file}'].update(disabled=False)
                    audio.Stop(file)
                else:
                    for key,val in window.key_dict.items():
                        if key != 'Stop::master' and 'Stop::' in str(key):
                            window.write_event_value(key, None)
                
            if 'Psr::' in event:
                file = event[5:]
                if file != 'master':
                    if audio.master_pause == False:
                        audio.Pause(file)
                        toggle_button_color(window[event])
                else:
                    audio.master_pause = not audio.master_pause
                    for key,val in window.key_dict.items():
                        if key != 'Psr::master' and 'Psr::' in str(key):
                            if audio.m_audio_map[key[5:]].playing == True:
                                audio.Pause(key[5:], paused=audio.master_pause)
                                toggle_button_color(window[key], rev=audio.master_pause)
                    toggle_button_color(window[event], audio.master_pause)
                    
            if 'Loop::' in event:
                file = event[6:]
                audio.Loop(file)
                
            if 'Ones::' in event:
                file = event[6:]
                audio.Clear_loop(file)

def toggle_button_color(item, rev=None):
    if rev == None:        
        btncolor = item.ButtonColor[::-1]
    elif rev == False:
        btncolor = sg.theme_button_color()
    else:
        btncolor = sg.theme_button_color()[::-1]
    
    item.update(button_color=btncolor)
    
    
def main(argv):
    folder = sg.popup_get_folder('Choose the folder containing your sounds')
    # folder = 'C:/Users/Bill/projects/DanMix/testsounds'
    if folder != None:
        #sg.popup(f'you chose {folder}')
        extensions = [ "*.mp3", "*.wav", "*.flac", "*.m4a" ]
        files = []
        for ext in extensions:
            files.extend(glob.glob(f'{folder}/{ext}'))
        layout, window = build_layout(files)
        audio = DanAudio(files)
        run_gui(layout, window, audio)
    else:
        sg.popup(f'no folder chosen: {folder}')
    
    

if __name__ == '__main__':
    main(sys.argv[1:])