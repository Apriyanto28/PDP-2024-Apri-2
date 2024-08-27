import time

def name_of_time(tm):
    hasil = ""
    waktu = ["detik", "menit", "jam"]
    i = 0
    while(tm > 0):
        tmp = tm % 60
        if(i >= len(waktu)):
            break
        hasil = f" {int(round(tmp))} {waktu[i]}" + hasil
        i += 1
        tm = tm // 60
    return hasil

wkt = time.time()
print(name_of_time(wkt))
