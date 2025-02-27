#!/usr/bin/env python
"""
Experiments with dawn, sunset and weather
"""
from pathlib import Path
import shutil

from clw.iconset import LocalIconSet


def main():
    # load the local pngs
    icons = LocalIconSet("png")
    codes = icons.load_weather_codes()
    # num / day,night / image
    for k, v in codes.items():
        for tod, entry in v.items():
            # mv image_file to src/clw/png
            image_file = Path("png",  entry['image'])
            to_path = Path("src/clw/png", entry['image'])
            #print(image_file, to_path)
            shutil.copyfile(image_file, to_path)



if __name__ == "__main__":
    main()
