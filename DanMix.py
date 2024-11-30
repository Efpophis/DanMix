#!/usr/bin/env python

import FreeSimpleGUI as sg
import pygame.mixer as Mixer
import sys, glob

def build_layout(files):
    master_controls = [
                    [sg.Slider((0,100), orientation='vertical', expand_y=True, enable_events=True, disable_number_display=True, key=f'Vol::master'),
                     sg.Text('    '),
                    sg.Slider((0,100), orientation='vertical', expand_y=True, default_value=50, enable_events=True, disable_number_display=True, key=f'Pan::master'), sg.Button('Center', key='Ctr::master', button_color='green')],
                    [sg.Text('Vol'), sg.Text('      Pan')],
                    [sg.HorizontalSeparator()],
                    [sg.Button('Mute All X', key='Mute::master'), sg.Button('Pause All ||', key=f'Psr::master', disabled=True)]
                     ]
    
    dyn_layout = []
    #layout = []
    
    rgid=1
    for file in files:
        #ff = f'{file}'
        #fpk = f'Play::{file}'
        dyn_layout.append([sg.Text(f'File: {file}')])
        dyn_layout.append([sg.Push(), 
                           sg.Button("Play |>", key=f'Play::{file}'), sg.Button("Pause ||", key=f'Psr::{file}', disabled=True), 
                           sg.Button("Stop []", key=f'Stop::{file}'), 
                           sg.Radio('One shot',group_id=rgid, default=True, enable_events=True, key=f'Ones::{file}'),
                           sg.Radio('Loop', group_id=rgid, key=f'Loop::{file}', enable_events=True),
                          sg.Push()])
        dyn_layout.append([sg.Button('Mute X', key=f'Mute::{file}'), sg.Text('Volume: 0'), 
                      sg.Slider((0,100), orientation='horizontal', enable_events=True, disable_number_display=True, key=f'Vol::{file}'),
                      sg.Text('100   |   Pan:   L'), 
                      sg.Slider((0,100), orientation='horizontal', default_value=50, disable_number_display=True, enable_events=True,               key=f'Pan::{file}'),
                      sg.Text('R'), sg.Button('Center', key=f'Ctr::{file}', button_color='green')])
        dyn_layout.append([sg.HorizontalSeparator()])
        rgid += 1
    
    layout = [[sg.Frame('Master Controls',  master_controls, expand_y=True ), sg.Frame('Sounds', dyn_layout )]] 
    
    layout.append([sg.Push(), sg.Button('Exit'), sg.Push()])
    
    window = sg.Window("DanMix D&D Sound Board", layout)
    
    return layout, window

class DanAudio:
    def __init__(self):
        # set up members here
        foo=1
        
    def Pan(self, file, val):
        print(f'PAN: {file} value == {val}\r\n')

    def Vol(self, file, val):
        print(f'VOL: {file} value = {val}\r\n')       

    def Mute(self,file):
        # needs to toggle
        print(f'Mute: {file}')
    
    def Play(self,file):
        print(f'Play: {file}')
    
    def Stop(self,file):    
        print(f'Stop: {file}')
    
    def Pause(self,file):
        # should also toggle
        print(f'Pause/Resume: {file}')
    
    def Loop(self,file):
        print(f'Loop {file}')
    
    def Clear_loop(self,file):
        print(f'OneShot: {file}')
    
def run_gui(layout, window):
    audio=DanAudio()
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        else:
            #print(f'event == {event}\r\n')            
            if 'Pan::' in event:
                file = event[5:]
                val = values[event]                
                if val == 50:
                    window[f'Ctr::{file}'].update(button_color='green')
                else:
                    window[f'Ctr::{file}'].update(button_color=sg.theme_button_color())
                    #do something to indicate balanced
                    #like disable the corresponding center button / change color
                audio.Pan(file, val)
            if 'Ctr::' in event:
                # center the corresponding pan slider   
                file = event[5:]
                print(f'Center: {file}')
                window[f'Pan::{file}'].update(value=50)
                window[event].update(button_color='green')
                audio.Pan(file, 50)
            if 'Vol::' in event:
                file = event[5:]
                val = values[event]
                audio.Vol(file, val)                
            if 'Mute::' in event:
                file = event[6:]                
                btncolor = window[event].ButtonColor
                window[event].update(button_color=btncolor[::-1])
                audio.Mute(file)
            if 'Play::' in event:
                file = event[6:]                
                btncolor = window[event].ButtonColor
                window[event].update(button_color=btncolor[::-1], disabled=True)
                window[f'Psr::{file}'].update(disabled=False)
                window['Psr::master'].update(disabled=False)
                audio.Play(file)
            if 'Stop::' in event:
                file = event[6:]                
                #if file != 'master':
                window[f'Play::{file}'].update(button_color=sg.theme_button_color(), disabled=False)
                window[f'Psr::{file}'].update(button_color=sg.theme_button_color(), disabled=True)
                audio.Stop(file)
            if 'Psr::' in event:
                file = event[5:]    
                btncolor = window[event].ButtonColor
                window[event].update(button_color=btncolor[::-1])
                audio.Pause(file)
                #print(btncolor)
            if 'Loop::' in event:
                file = event[6:]
                audio.Loop(file)
            if 'Ones::' in event:
                file = event[6:]
                audio.Clear_loop(file)
            
    
def main(argv):
    #folder = sg.popup_get_folder('Choose the folder containing your sounds')
    folder = 'C:/projects/DanMix/testsounds'
    if folder != None:
        #sg.popup(f'you chose {folder}')
        files = glob.glob(f'{folder}/*.mp3')
        layout, window = build_layout(files)
        run_gui(layout, window)
    else:
        sg.popup(f'no folder chosen: {folder}')
    
    

if __name__ == '__main__':
    main(sys.argv[1:])