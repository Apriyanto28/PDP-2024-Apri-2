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
citra_hasil_deblurring = ""
citra_hasil_denoising = ""

## Mendapatkan nama file citra
arr_citra_awal = get_image_files(citra_awal)
arr_citra_hasil_deblurring = get_image_files(citra_hasil_deblurring)
arr_citra_hasil_denoising = get_image_files(citra_hasil_denoising)