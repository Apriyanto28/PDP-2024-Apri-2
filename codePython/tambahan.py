import subprocess
import os
import glob
from PIL import Image
import time

def get_image_files(directory):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))
    return image_files

## Lokasi Citra
citra_awal = ""

## Mendapatkan nama file citra
arr_citra_awal = get_image_files(citra_awal)

## Nama hasil proses
name = "result"
