# DanMix
D&amp;D Sound effects player / mixer

## Overview
This is a simple GUI program written in Python to play multiple audio files simultaneously.
If you download a release ZIP file, you should be able to run it on Windows, which
is the target platform.  Otherwise, you can run it with a python interpreter on any
platform, or build it yourself with PyInstaller, or whatever.

## Installation

### Windows
1. Download the `DanMix.zip` from the latest release
2. Extract the .EXE file and put it anywhere you like
3. Run the EXE file like you usually would

### Other
Assuming you have a sane python environment, you can run the script directly.
If you're going to do this, you'll need to have the following modules installed:
```
freesimplegui
pygame
```
1. Clone this repository
2. From a command prompt, run `python DanMix.py` or `./DanMix.py`
3. Install any missing libraries it complains about
3. If you want, you can try to make a binary using PyInstaller:
    * python -m PyInstaller --onefile --noconsole DanMix.py

## Instructions

First, prepare a directory with all the different audio files you want to use. The
program supports `mp3, wav, flac, and m4a` currently, but could probably be expanded
to support others.

When you load the program, you'll be prompted to choose a folder. Browse or enter the path
to your files and hit `Ok`.

After that, playing, mixing, pausing, etc. should be fairly intuitive.

## Releases
See the [Releases](https://github.com/Efpophis/DanMix/releases) page for the latest.

## Support
Use the Source, Luke!
