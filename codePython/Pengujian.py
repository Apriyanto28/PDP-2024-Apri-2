import os
import numpy as np
import pandas as pd
import cv2

# Mendapatkan semua nama gambar dalam 1 folder
def get_image_files(directory):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))
    return image_files

# Melakukan pengecekan noise
def check_noise(mask, threshold):
    #print(mask)
    # get center pixel
    pixel_value = mask[1, 1]

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

# Mendapatkan jumlah noise pada citra
def get_sum_of_noise(img, w, h):
    img_pad = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
    mask = []

    noise = 0
    for x in range(h):
        for y in range(w):
            for c in range(3):
                mask = img_pad[x : x + 3, y : y + 3][c]

                if(check_noise(mask, 20)):
                    noise += 1
    
    return noise

# Mengecek apakah gambar termasuk blur atau tidak
# contoh threshold = 100
def is_image_blurry(image, threshold):
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Compute the Laplacian of the image and then the variance
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
    variance = laplacian.var()
    
    # Determine if the image is blurry based on the threshold
    if variance < threshold:
        return True
    else:
        return False

# Lokasi Citra
citra_awal = "D:\\OneDrive - mikroskil.ac.id\\(1) PDP\\2324Genap\\Jurnal-Image-Enhancement\\dataset\\awal-ubuntu"
citra_hasil_deblurring = "D:\\OneDrive - mikroskil.ac.id\\(1) PDP\\2324Genap\\Jurnal-Image-Enhancement\\dataset\\Hasil-Deblurring"
citra_hasil_denoising = "D:\\OneDrive - mikroskil.ac.id\\(1) PDP\\2324Genap\\Jurnal-Image-Enhancement\\dataset\\Hasil-Denoising"

# Mendapatkan nama file citra
arr_citra_awal = get_image_files(citra_awal)
arr_citra_hasil_deblurring = get_image_files(citra_hasil_deblurring)
arr_citra_hasil_denoising = get_image_files(citra_hasil_denoising)

# Mendapatkan jumlah citra
jumlah_citra = len(arr_citra_awal)

# Membuat dataframe
data = {}
df = pd.DataFrame(data)

# Deklarasi Array untuk Penyimpanan Data

## Nilai awal
name_of_image = []
sum_of_pixel = []

## Before
check_blur_before = []
noise_before = []
persen_noise_before = []

## After (Deblurring)
check_blur_after1 = []
noise_after1 = []
persen_noise_after1 = []

## After (Denosing)
check_blur_after2 = []
noise_after2 = []
persen_noise_after2 = []

#Nilai awal dan akhir proses
awal = 10
akhir = 40

# Memproses citra
for i in range(awal, akhir):

    # Mendapatkan nama citra
    image_name = os.path.basename(arr_citra_awal[i])
    name_of_image += [image_name]
    print(f"Citra ke-{i}: {image_name}")

    ## Citra Awal

    # Membaca citra
    img = cv2.imread(arr_citra_awal[i])

    # Mendapatkan detail dari citra
    h = img.shape[0]
    w = img.shape[1]
    c = img.shape[2]

    # Mendapatkan jumlah piksel 
    ttl_piksel = h * w * c
    sum_of_pixel += [ttl_piksel]

    # Mengecek apakah citra termasuk citra kabur atau tidak
    blur = "blur image" if is_image_blurry(img, 100) else "non-blur image"
    check_blur_before += [blur]

    # Mendapaktan jumlah noise
    sum_noise = get_sum_of_noise(img, w, h)
    noise_before += [sum_noise]

    # Mengkonversi jumlah noise menjadi persen
    persen = sum_noise / ttl_piksel * 100
    persen_noise_before += [f"{persen}%"]

    
    ## Citra setelah Deblurring

    # Membaca citra
    img = cv2.imread(arr_citra_hasil_deblurring[i])

    # Mengecek apakah citra termasuk citra kabur atau tidak
    blur = "blur image" if is_image_blurry(img, 100) else "non-blur image"
    check_blur_after1 += [blur]

    # Mendapaktan jumlah noise
    sum_noise = get_sum_of_noise(img, w, h)
    noise_after1 += [sum_noise]

    # Mengkonversi jumlah noise menjadi persen
    persen = sum_noise / ttl_piksel * 100
    persen_noise_after1 += [f"{persen}%"]

    
    ## Citra setelah Denoising

    # Membaca citra
    img = cv2.imread(arr_citra_hasil_denoising[i])

    # Mengecek apakah citra termasuk citra kabur atau tidak
    blur = "blur image" if is_image_blurry(img, 100) else "non-blur image"
    check_blur_after2 += [blur]

    # Mendapaktan jumlah noise
    sum_noise = get_sum_of_noise(img, w, h)
    noise_after2 += [sum_noise]

    # Mengkonversi jumlah noise menjadi persen
    persen = sum_noise / ttl_piksel * 100
    persen_noise_after2 += [f"{persen}%"]

# Memasukkan Data ke dalam Excel

## Detail awal
df["Nama Citra"] = name_of_image
df["Jumlah Piksel Citra"] = sum_of_pixel

## Citra Awal
df["Blur Awal"] = check_blur_before
df["Noise Awal"] = noise_before
df["Persen Noise Awal"] = persen_noise_before

## Setelah Deblurring
df["Blur Deblurring"] = check_blur_after1
df["Noise Deblurring"] = noise_after1
df["Persen Noise Deblurring"] = persen_noise_after1

## Setelah Denoising
df["Blur Denoising"] = check_blur_after2
df["Noise Denoising"] = noise_after2
df["Persen Noise Denoising"] = persen_noise_after2

# Menyimpan data ke Excel
df.to_excel('result1.xlsx', sheet_name='Sheet1', index=False)
print("\nData Berhasil disimpan di Excel")