# importing the modules
import cv2
from imutils import build_montages
from dbConnect import koneksi
import json
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

db = koneksi()
mycursor = db.cursor()
import os
from os import path
def crop_center(img,cropx,cropy):
    y,x,z = img.shape
    startx = x//2-(cropx//2)
    # starty = y//2-(cropy//2)
    starty = 0    
    return img[starty:starty+cropy,startx:startx+cropx]

def gabung(asal,tujuan,kelas):
    list_gambar = []
    images = os.listdir(asal)
    for imagePath in images:
        nama = os.path.join(asal,imagePath)
        image = cv2.imread(nama)
        if image.shape[0] < image.shape[1]:
            terkecil = image.shape[0]
        else:
            terkecil = image.shape[1]
        croped = crop_center(image,terkecil,terkecil)
        list_gambar.append(croped)
    montages = ''
    montages = build_montages(list_gambar, (200, 200), (4, 4))
    i = 1 
    path_akhir = os.path.join(tujuan,kelas)
    if not path.exists(path_akhir):
        os.mkdir(path_akhir)
    path_akhir_gambar = os.path.join(path_akhir,'gambar')
    if not path.exists(path_akhir_gambar):
        os.mkdir(path_akhir_gambar)
    for montage in montages:
        status= cv2.imwrite("{}\\{}.jpg".format(path_akhir_gambar,i), montage)
        # print(status)
        i+=1
    mycursor.execute("SELECT m.nrp_mahasiswa,m.nama_mahasiswa "
                "FROM mahasiswa as m, kelas as k where k.id_kelas = m.id_kelas and k.nama_kelas = '"+ kelas +"' order by m.nrp_mahasiswa")
    data = mycursor.fetchall()
    path_akhir_json = os.path.join(path_akhir,'info')
    if not path.exists(path_akhir_json):
        os.mkdir(path_akhir_json)
    panjang_data = len(data)
    if len(data) == 1:
        data_terakhir = data[0][0]
    else:
        data_terakhir = data[-1][0]
    datake = 0
    if len(data) <= 16:
        batas = 1
    else:
        batas = 2
    for i in range(batas):
        FullFileName = str(i+1) + ".jpg.json"
        datajson = {}
        datajson["Last Modified"] = dt_string
        datajson["File Name"] = FullFileName
        datajson["Mahasiswa"] = []
        for j in range(16):
            NRP = data[i*16+j][0]
            NAMA = data[i*16+j][1]
            datajson["Mahasiswa"].append({"NRP":NRP,"Nama":NAMA})
            datake += 1
            if datake == len(data):
                for i in range(datake,32):
                    datajson["Mahasiswa"].append({"NRP":'',"Nama":''})
                with open("{}\\{}".format(path_akhir_json,FullFileName), "w") as write_file:
                    json.dump(datajson, write_file)
                break    
        with open("{}\\{}".format(path_akhir_json,FullFileName), "w") as write_file:
            json.dump(datajson, write_file)
