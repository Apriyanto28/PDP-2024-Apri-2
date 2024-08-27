import cv2
import os

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

## Lokasi simpan hasil citra
lok_simpan = ""

## Mendapatkan nama file citra
arr_citra_awal = get_image_files(citra_awal)

## Nama hasil proses
name = "result"

## Proses pergantian nama file
for i in range(len(arr_citra_awal)):

    # Untuk membaca gambar
    img = cv2.imread(arr_citra_awal[i])

    # Untuk lokasi dan nama file yang mau disimpan
    hasil = lok_simpan + "\\" + name + "\\" + str(i) + ".png"

    # Untuk menyimpan hasil perubahan nama citra
    cv2.imwrite(img, hasil)