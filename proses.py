import os
import cv2
import shutil
import boto3
import csv
import math
import json
with open('cred.csv','r')as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[2]
        secret_access_key = line[3]
client = boto3.client('rekognition',
                        aws_access_key_id = access_key_id,
                        aws_secret_access_key = secret_access_key)
tinggi_resized = 500
font = cv2.FONT_HERSHEY_DUPLEX
from datetime import datetime

def resize(pic):
    height = int(tinggi_resized)
    width = int(pic.shape[1] / pic.shape[0] * height)
    dim = (width, height)
    ret = cv2.resize(pic, dim, interpolation=cv2.INTER_AREA)
    return ret

def proses_hasil_capture(nama_sesi,kelas):
    folder_capture = 'static/file/proses/capturan/'+nama_sesi
    folder_buffer = 'static/file/proses/buffer/'+nama_sesi
    folder_tampung = 'static/file/proses/tampung/'+nama_sesi
    folder_dataset = 'static/file/upload/dataset/gabung/'+kelas
    picture_list = os.listdir(folder_capture)
    list_semua_mhs = list()
    final_list = list()
    for pic in picture_list:
        print("-----------{}--------".format(pic))
        # print("{} -> {}".format(folder_capture, x))
        captured_time = pic[-12:-4]
        buffer(folder_capture,folder_buffer,pic)
        jumlah = cariwajah(folder_buffer,folder_tampung,pic)
        if jumlah >= 1:
            list_deteckted = comparesemua(folder_dataset,folder_tampung,nama_sesi,kelas)
            for mhs in list_deteckted:
                if mhs not in list_semua_mhs:
                    # print('mahasiswa--------------'+mhs)
                    list_semua_mhs.append(mhs)
                    final_list.append((mhs,captured_time))
        # print("------------")

    # print(list_semua_mhs)
    # print(final_list)
    tulisjson(nama_sesi,final_list)

def buffer(path,tujuan,pic):
    picpath = path + "/" + pic
    img = cv2.imread(picpath)
    color = [255, 255, 255]
    top, bottom, left, right = [20] * 4
    img_with_border = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    dirpath = os.path.join(tujuan)
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(tujuan)
    cv2.imwrite(tujuan + '/'+pic, img_with_border)
    # return img_with_border

def cariwajah(input,tampung,pic):
    # print("mencari wajah")
    inputGambar = os.path.join(input,pic)
    with open(inputGambar, 'rb') as source_image:
        foto_cari_byte = source_image.read()
    response = client.detect_faces(
        Image={'Bytes': foto_cari_byte},
        Attributes=['ALL']
    )
    i=1
    gambar = cv2.imread(inputGambar)
    gambar = resize(gambar)
    dirpath = tampung
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)
    # print("Menemukan {} wajah".format(len(response['FaceDetails'])))
    for faceDetail in response['FaceDetails']:
        location = faceDetail["BoundingBox"]
        left = math.floor(location["Left"] * gambar.shape[1]-10)
        top = math.floor(location["Top"] * gambar.shape[0]-10)
        width = math.floor(location["Width"] * gambar.shape[1]+20)
        height = math.floor(location["Height"] * gambar.shape[0]+20)
        pic = gambar[top:top + height, left:left + width]
        pic = resize(pic)
        cv2.imwrite(tampung+'/temp-{}.jpg'.format(i), pic)
        cv2.rectangle(gambar, (left, top), (left + width, top + height), (255, 0, 0), 2)
        # cv2.rectangle(gambar, (left, (top+height) - 35), (left+width, top+height), (0, 0, 255), cv2.FILLED)
        cv2.putText(gambar, str(i), (left + 6, top+height - 6), font, 0.5, (255, 255, 255), 1)
        i = i+1;
    # cv2.imshow("Target image",gambar)
    cv2.waitKey(1)
    return len(response['FaceDetails'])

def comparesemua(dataset,tampung,sesi,kelas):
    # print("membandingkan wajah")
    tampungan = os.listdir(tampung)
    datasetkumpulangambar = os.listdir(dataset + "/" + "gambar")
    datasetkumpulaninfo = os.listdir(dataset + "/" + "info")

    i = 1
    list_nama = list()
    for wajah in tampungan:
        j = 1
        # print('compare wajah {}'.format(i))
        for data in datasetkumpulangambar:
            with open(tampung + '/' + wajah, 'rb') as source_image:
                source_byte = source_image.read()
            with open(dataset + '/gambar/' + data, 'rb') as source_image:
                target_byte = source_image.read()
            try:
                response = client.compare_faces(
                    SourceImage={'Bytes': source_byte},
                    TargetImage={'Bytes': target_byte},
                    SimilarityThreshold=90
                )
                with open(dataset + '/info/' + data + '.json') as json_file:
                    data_json = json.load(json_file)
                target = cv2.imread(dataset + '/gambar/' + data)
                target_resized = resize(target)
                if len(response["FaceMatches"]) > 0:
                    for match in response["FaceMatches"]:
                        similarity = match["Similarity"]
                        Face = match["Face"]["BoundingBox"]
                        left = math.ceil(Face["Left"] * target_resized.shape[1] - 10)
                        top = math.ceil(Face["Top"] * target_resized.shape[0] - 10)
                        width = math.ceil(Face["Width"] * target_resized.shape[1] + 20)
                        height = math.ceil(Face["Height"] * target_resized.shape[0] + 20)
                        detail = cari_nama(Face, target_resized, data_json, (left, top, width, height))
                        list_nama.append(detail['NRP'])
                        print('Menemukan NRP {} Nama {} dengan similarity {}'.format(detail['NRP'],
                                                                                                     detail['Nama'],
                                                                                                     similarity))
                        cv2.rectangle(target_resized, (left, top), (left + width, top + height), (255, 0, 0), 3)
                        cv2.putText(target_resized, str(i), (left + 6, top + height - 6), font, 0.5, (255, 255, 255), 1)
                #     cv2.imshow("wajah {} target {}".format(i, j), target_resized)
                # cv2.moveWindow("wajah {} target{}".format(i,j), (i*300)+600, (j*100)+400)
                j = j + 1
                # cv2.waitKey(10)
            except Exception:
               print("gagal mencari wajah2")
        i = i+1
    print("selesai dengan gambar ini")
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    return list_nama

def cari_nama(Face,target_resized,data_json,lokasi):
    left, top, width, height = lokasi
    tinggigambar = round(target_resized.shape[0]/4)
    lebargambar = round(target_resized.shape[1]/4)
    kolom = 0
    baris = 0
    for i in range(4):
        if Face['Left'] < (0.25*i)+0.25:
            break
        kolom = kolom + 1
    for i in range(4):
        if Face['Top'] < (0.25*i)+0.25:
            break
        baris = baris + 1
    indek = baris*4 + kolom
    mahasiswa = data_json['Mahasiswa'][indek]
    if baris > 2:
        atas = round(baris * tinggigambar)
        tinggi = round(tinggigambar/4)
        selisih = round(atas+height) - top
        atas = round(atas - selisih/2)
    else:
        atas = baris * tinggigambar + round(2*tinggigambar/4)
        selisih = (top+height)-atas
        atas = selisih + atas
        tinggi = round(tinggigambar/4) + selisih

    kiri = kolom * lebargambar
    lebar = lebargambar
    cv2.rectangle(target_resized, (kiri, atas), (kiri + lebar,atas+tinggi), (0, 255, 0),cv2.FILLED)
    cv2.putText(target_resized, str(mahasiswa['Nama']), (kiri + 6, atas + 15), font, 0.3, (0, 0, 0), 1)
    cv2.putText(target_resized, str(mahasiswa['NRP']), (kiri + 6, atas + 30), font, 0.3, (0, 0, 0), 1)
    return mahasiswa

def tulisjson(nama_sesi,final_list):
    record_path = 'static/file/record/'+nama_sesi
    if os.path.exists(record_path) and os.path.isdir(record_path):
        pass
    else:
        os.makedirs(record_path)
    current_record_path = record_path 
    if os.path.exists(current_record_path) and os.path.isdir(current_record_path):
        pass
    else:
        os.makedirs(current_record_path)
    date = nama_sesi[-19:-9]
    # print(date)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    fileName = "Record_" +nama_sesi
    FullFileName =  fileName + ".json"
    data = {}
    data["Last Modified"] = dt_string
    data["File Name"] = fileName
    data["Sesi Absensi"] = nama_sesi
    data["Absensi"] = []
    if os.path.exists(current_record_path +"/"+ FullFileName):
        # print("file sudah ada & membaca file")
        with open(current_record_path +"/"+ FullFileName) as json_file:
            data_load = json.load(json_file)
        data["Absensi"] = data_load['Absensi']
        list_mhs = []
        for mhs in data["Absensi"]:
            list_mhs.append(mhs['NRP'])

        for new_mhs in final_list:
            if new_mhs[0] not in list_mhs:
                # print('menambah {}'.format(new_mhs[0]))
                NRP = new_mhs[0]
                waktu = new_mhs[1]
                tanggal = date
                data['Absensi'].append({"NRP": NRP, "waktu": waktu,"tanggal": tanggal})
    else:
        print("file belum ada")
        for x in final_list:
            # print("menulis nama baru")
            NRP = x[0]
            waktu = x[1]
            tanggal = date
            data["Absensi"].append({"NRP": NRP, "waktu": waktu,"tanggal": tanggal})
    # print(data)
    # print(data['Absensi'][0]["NRP"])
    #
    with open(current_record_path +"/"+ FullFileName, "w") as write_file:
        json.dump(data, write_file)
