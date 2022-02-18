#!/bin/bash

pipInstall() {
    yes | pip install "$1" --disable-pip-version-check --quiet --upgrade
}

pipInstall "Pillow"
pipInstall "numpy"
pipInstall "potracer"
pipInstall "pyclipper"
pipInstall "svgutils"