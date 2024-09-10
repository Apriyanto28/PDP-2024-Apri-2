import cv2
import numpy as np
import os

# Load image from folder
def get_image_files(directory):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))
    return image_files

# Folder image 1
img_loc_1 = "D:\\OneDrive - mikroskil.ac.id\\(1) PDP\\2324Genap\\Hasil Pengujian\\citra_uji"
arr_res_1 = get_image_files(img_loc_1)

# Folder image 2
img_loc_2 = "D:\\OneDrive - mikroskil.ac.id\\(1) PDP\\2324Genap\\Hasil Pengujian\\citra_hasil"
arr_res_2 = get_image_files(img_loc_2)

total_img = len(arr_res_1)

for i in range(total_img):
    img_1 = os.path.basename(arr_res_1[i])
    img_2 = os.path.basename(arr_res_2[i])
    if(img_1 != img_2):
        print(f"Citra ke-{i} = {img_1}")
        break