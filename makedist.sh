#!/bin/bash

rm -rf dist
rm -rf build
rm -rf *.spec

winpty python -m PyInstaller --onefile --noconsole DanMix.py