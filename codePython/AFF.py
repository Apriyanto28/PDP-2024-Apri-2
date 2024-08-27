# referensi: https://www.geeksforgeeks.org/python-opencv-getting-and-setting-pixels/

import cv2
import math

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

def cek_noise(mask):
    Xp = mask[1][1]
    rata = 0

    for i in range(3):
        for j in range(3):
            if(i != 1 and j != 1):
                rata = rata + mask[i][j]
    rata = rata / 8

    return abs(math.floor(rata) - Xp) >= 30

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

## Read Image
img = cv2.imread("Lokasi Citra")
print(f"Bentuk citra:\nTinggi Citra: {img.shape[0]}\nLebar Citra: {img.shape[1]}\nTChannel Citra: {img.shape[2]}\n")

## Get the image detail [ height, width, channel ]
h = img.shape[0]
w = img.shape[1]

## Declare Variabel
hsl_img = img[:]
mask = []
rata = 0
rata2 = 0
m_X = 0
m_k_x = [0] * 16
A_f = 0

## Get Masking from the Image
for x in range(h):
    for y in range(w):

        hsl = [0, 0, 0]
        print(f"x = {x}, y = {y}")
        for c in range(3):
            mask = get_mask(img, x, y, c, h, w)

            if(not(cek_noise(mask))):
                print(f"Channel ke-{c}: Skip")
                continue

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

cv2.imwrite("Lokasi Simpan Citra", hsl_img)