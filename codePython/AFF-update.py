# referensi: https://www.geeksforgeeks.org/python-opencv-getting-and-setting-pixels/

import numpy as np
import cv2
import math
import os
from PIL import Image
import time
import pandas as pd
import openpyxl

# Get sum noise after process
def get_sum_noise(img, h, w, c):
    count = 0
    for x in range(h):
        for y in range(w):
            for cc in range(c):
                mask = get_mask2(img, x, y, cc)
                if(cek_noise3(mask, 20)):
                    count = count + 1
    return count

# Get the name of time
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

# function to get all image in directory
def get_image_files(directory):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))
    return image_files

# Function to check noise in image
# threshold = 2.0
def cek_noise2(mask, threshold):
    # Calculate the local mean and variance
    local_mean = np.mean(mask)
    local_variance = np.var(mask)

    # Calculate the standard deviation
    local_std = np.sqrt(local_variance)

     # Get the pixel value
    pixel_value = mask[1][1]

    # Determine if the pixel is noise
    if abs(pixel_value - local_mean) > threshold * local_std:
        return True
    return False

# threshold = 20
def cek_noise3(mask, threshold):
    # get center pixel
    pixel_value = mask[1][1]

    # delete center pixel
    #print(mask)
    mask = np.delete(mask, len(mask)//2)
    #print(mask)

    # get median value
    median_value = np.median(mask)

    if(abs(pixel_value - median_value) > threshold):
        return True
    else:
        return False

def cek_noise(mask):
    Xp = mask[1][1]
    rata = 0

    for i in range(3):
        for j in range(3):
            if(i != 1 and j != 1):
                rata = rata + mask[i][j]
    rata = rata / 8

    return abs(math.floor(rata) - Xp) >= 30

# function to get mask of pixel
def get_mask2(img, x, y, c):
    padded_image = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
    
    mask = []
    for i in range(x, x + 3):
        tmp = []
        for j in range(y, y + 3):
            tmp = tmp + [padded_image[i, j, c]]
        mask = mask + [tmp]
    return mask

def get_mask(img, x, y, c, h, w):
    # x = h = height
    # y = w = width

    hasil = []
    for i in range(3):
        tmp = []
        for j in range(3):
            tmp = tmp + [0]
        hasil = hasil + [tmp]

    if(x == 0):
        if(y == 0):
            hasil[0][0] = img[0, 0, c]
        elif(y == w - 1):
            hasil[0][2] = img[0, w - 1, c]
        else:
            hasil[0][1] = img[0, y, c]
    elif(x == h - 1):
        if(y == 0):
            hasil[2][0] = img[h - 1, 0, c]
        elif(y == w - 1):
            hasil[2][2] = img[h - 1, w - 1, c]
        else:
            hasil[2][1] = img[h - 1, y, c]
    else:
        if(y == 0):
            hasil[1][0] = img[x, 0, c]
        elif(y == w - 1):
            hasil[1][2] = img[x, w - 1, c]
        else:
            hasil[1][1] = img[x, y, c]
    
    return hasil

# function for AFF
def get_mean(arr):
    hsl = 0
    for i in range(3):
        for j in range(3):
            hsl = hsl + arr[i][j]
    return hsl / 9

def get_mean2(arr):
    hsl = 0
    for i in range(3):
        for j in range(3):
            if(not(i == 1 and j == 1)):
                hsl = hsl + arr[i][j]
    return hsl / 8

def meanFS(n):
    a = 0
    b = 3
    c = 252
    d = 255

    if (n > a and n < b):
        return (n - a) / 3
    elif (n >= b and n <= c):
        return 1
    elif (n > c and n < d):
        return (d - n) / 3
    else:
        return 0;

def mX(arr):
    Trap = 0
    m_X = arr[1][1]
    ttl1 = 0
    ttl2 = 0

    for i in range(3):
        for j in range(3):
            Trap = meanFS(arr[i][j])
            ttl1 = ttl1 + arr[i][j] * Trap
            ttl2 = ttl2 + Trap
    
    if(ttl2 > 0):
        m_X = ttl1 / ttl2
    return m_X

def Gk(x, k):
    if (k == 0):
        if (x <= 14):
            return 1
        elif (x > 14 and x < 17):
            return (17 - x) / 3
        else:
            return 0
    elif (k == 15):
        if (x >= 241):
            return 1
        elif (x > 238 and x < 241):
            return (241 - x) / 3
        else:
            return 0
    else:
        a = k * 16 - 2
        b = k * 16 + 1
        c = (k + 1) * 16 - 2
        d = (k + 1) * 16 + 1

        if (x > a and x < b):
            return (x - a) / 3
        elif (x >= b and x <= c):
            return 1
        elif (x > c and x < d):
            return (d - x) / 3
        else:
            return 0

def mKX(arr):
    Xp = arr[1][1]
    m_KX = [0] * 16

    for k in range(16):
        m_KX[k] = Xp
        ttl1 = 0
        ttl2 = 0
        g_k = 0

        for i in range(3):
            for j in range(3):
                g_k = Gk(arr[i][j], k)
                ttl1 = ttl1 + arr[i][j] * g_k
                ttl2 = ttl2 + g_k
        
        if(ttl2 > 0):
            m_KX[k] = ttl1 / ttl2
    return m_KX

def Af(m_x, m_k_x):
    min_k = abs(m_x - m_k_x[0])
    ind = 0

    for i in range(1, 16):
        tmp = abs(m_x - m_k_x[i])
        if(min_k > tmp):
            min_k = tmp
            ind = i
    
    return m_k_x[ind]

# declare variable name for excel
data = {}

# using pandas to create dataframe
df = pd.DataFrame(data)

### Ubah bagian ini disesuaikan dengan lokasi folder gambar berada
#Contoh: img_loc = "D:\\OneDrive - mikroskil.ac.id\\(1) PDP\\2324Genap\\DatasetProcess\\Deblurring\\Apri"
img_loc = "D:\\HasilDebluring\\Process\\Apri"

### Ubah bagian ini disesuaikan dengan lokasi folder tempat gambar disimpan
#Contoh: save_fol_loc
save_fol_loc = "D:\\HasilDebluring\\Process\\Apri-Hasil"


### Ini disesuaikan kembali mau mulai dari gambar ke berapa sampai ke berapa
mulai = 260
akhir = 345

# Get all image in folder
img_file = get_image_files(img_loc)

# declare variabel in array to save in dataframe
name_of_image = []
sum_of_pixel = []
total_of_noise = []
percent_of_noise = []
process_of_time = []

total_of_noise_after = []
percent_of_noise_after = []

j = 0
for i in range(mulai, akhir):
    # to count the time start of the process
    time_start = time.time()

    # name for file to save and location
    name_of_image += [os.path.basename(img_file[i])]
    ress = save_fol_loc + "\\" + name_of_image[j]
    img = cv2.imread(img_file[i])
    
    # get the detail of image and print
    print(f"Proses Citra ke-{i} = {name_of_image[j]}", end = "")
    #print(f"Bentuk citra: {img.shape[0]} x {img.shape[1]} x {img.shape[2]} => ", end = "")
    
    ## get the image detail [ height, width, channel ]
    hh = img.shape[0]
    ww = img.shape[1]
    cc = img.shape[2]

    # get the total of pixel image
    sum_of_pixel += [ww * hh * cc]
    # print(f"Sum of pixel = {sum_of_pixel}")
    
    ## Declare Variabel
    hsl_img = img[:]
    mask = []
    rata = 0
    rata2 = 0
    m_X = 0
    m_k_x = [0] * 16
    A_f = 0

    # for count the noise
    count = 0

    # Processing Image
    for x in range(hh):
        for y in range(ww):
            hsl = [0, 0, 0]
            
            for c in range(cc):
                ## Get Masking from the Image
                #mask = get_mask(img, x, y, c, hh, ww)
                mask = get_mask2(img, x, y, c)

                # Check noise with threshold 3.0
                threshold = 20
                if(not(cek_noise3(mask, threshold))):
                    hsl[c] = mask[1][1]
                    continue

                #count the total of noise in image
                count = count + 1
                
                rata = get_mean(mask)
                rata2 = get_mean2(mask)
                m_k_x = mKX(mask)

                Xp = img[x, y, c]
                m_X = mX(mask)
                A_f = Af(m_X, m_k_x)

                hsl[c] = Xp
                if(math.floor(abs(rata2 - Xp)) >= 250):
                    hsl[c] = int(math.floor(rata2))
                elif(math.floor(abs(rata - m_X)) < 128):
                    hsl[c] = int(math.floor(m_X))
                else:
                    hsl[c] = int(math.floor(A_f))
            hsl_img[x, y] = [hsl[0], hsl[1], hsl[2]]

    # get the time for end of process
    end_time = time.time()
    length_process = end_time - time_start

    #print(f"Sum of noise = {count} of {sum_of_pixel} = {count / float(sum_of_pixel) * 100}%")
    #print(f"Waktu untuk Proses = {name_of_time(length_process)}\n")

    total_of_noise += [count]
    
    percent_of_noise += [f"{round(count / float(sum_of_pixel[j]) * 100, 3)}%"]
    process_of_time += [name_of_time(length_process)]
    print(f" = {process_of_time[j]}")

    #tmp_count = get_sum_noise(hsl_img, ww, hh, cc)

    #total_of_noise_after += [tmp_count]
    #percent_of_noise_after += [f"{round(tmp_count / float(sum_of_pixel[j]) * 100, 3)}%"]
    cv2.imwrite(ress, hsl_img)

    j = j + 1

# insert data into data frame
df['image_name'] = name_of_image # get all image name
df['total_pixel_image'] = sum_of_pixel # get all total of pixel
df['total_noise'] = total_of_noise # get all total noise
df['percent_noise'] = percent_of_noise # convert all total of noise into percent with 3 decimal place
df['process_time'] = process_of_time # get all the time of process image

df['total_noise_after'] = total_of_noise_after # get all the time of process image
df['percent_noise_after'] = percent_of_noise_after # get all the time of process image

# save in excel file
df.to_excel('result.xlsx', sheet_name='Sheet1', index=False)

print("sudah berhasil disimpan ke dalam excel")