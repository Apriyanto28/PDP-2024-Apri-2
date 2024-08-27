import subprocess
import os
import glob
from PIL import Image
import time

def name_of_time(tm):
    hasil = ""
    waktu = ["second", "minute", "hour"]
    i = 0
    while(tm > 0):
        tmp = tm % 60
        if(i >= len(waktu)):
            break
        hasil = f" {int(round(tmp))} {waktu[i]}" + hasil
        i += 1
        tm = tm // 60
    return hasil

def get_image_files(directory):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))
    return image_files

## Directory Location and filename image file
#file_name = "codeDeblurImage/ezgif-frame-050.jpg"

## Directory Name [source]
dir_name = "/home/apriyanto/Documents/DatasetBaru/train/images"

## Directory Result Location
res_loc = "/home/apriyanto/Documents/DatasetBaru/train-res-deconv"

# Making directory
if(not(os.path.exists(res_loc))):
    os.makedirs(res_loc)

## Filename Result
file_name_res = "result"

## Declare variabel
com = [""] * 6
com1 = [""] * 6

# command
com[0] = "sudo"
com1[0] = "sudo"


image_file_arr = get_image_files(dir_name)

awal = 0
akhir = len(image_file_arr)

for i in range(awal, akhir):
    image_file = image_file_arr[i]
        
    print(f"Proses Citra ke-{i} = {image_file}")
        
    #Estimate the kernel
    file_name = dir_name + "/" + image_file
    com[1] = "codeDeblurImage/estimate-kernel" # command estimate kernel
    com[2] = str(7) # kernel size
    com[3] = file_name # filename to process
    com[4] = res_loc + "/" + "kernel-" + str(i) + ".tif" # kernel name and location directory
    com[5] = "--no-multiscale"
    subprocess.run(com)

    ## Deblurring Image
    com1[1] = "codeDeblurImage/deconv" # command deblurring image
    com1[2] = file_name # filename to process
    com1[3] = res_loc + "/" + "kernel-" + str(i) + ".tif" # kernel name and location directory
    com1[4] = res_loc + "/" + file_name_res + "-" + str(i) + ".png" # result file
    com1[5] = "--alpha=" + str(9)
    subprocess.run(com1)

## Untuk pengujian
'''
## run the iteration
for i in range(1, 51, 2):
    ## example command
    ## ./estimate-kernel 15 hollywood.jpg kernel.tif
    ## ./deconv hollywood.jpg kernel.tif deblurred.png
    
    print(f"Proses lambda-{i}")

    ## Estimate Kernel
    com[1] = "codeDeblurImage/estimate-kernel" # command estimate kernel
    com[2] = str(7) # kernel size
    com[3] = file_name # filename to process
    com[4] = res_loc + "/" + "kernel.tif" # kernel name and location directory
    com[5] = "--no-multiscale"
    

    # run the command
    subprocess.run(com)

    ## Deblurring Image
    com1[1] = "codeDeblurImage/deconv" # command deblurring image
    com1[2] = file_name # filename to process
    com1[3] = res_loc + "/" + "kernel.tif" # kernel name and location directory
    com1[4] = res_loc + "/" + file_name_res + "-" + str(i) + ".png" # result file
    com1[5] = "--alpha=" + str(i)

    # run the command
    subprocess.run(com1)
'''