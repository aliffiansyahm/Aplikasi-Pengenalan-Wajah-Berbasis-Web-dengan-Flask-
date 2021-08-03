from dbConnect import koneksi
import os
import shutil
db = koneksi()
mycursor = db.cursor()

folder_path = "static/file"

if os.path.exists(folder_path):
    shutil.rmtree(folder_path)


os.mkdir("static/file")
os.mkdir("static/file/proses")
os.mkdir("static/file/proses/buffer")
os.mkdir("static/file/proses/capturan")
os.mkdir("static/file/tampung")
os.mkdir("static/file/record")
os.mkdir("static/file/upload")
os.mkdir("static/file/upload/dataset")
os.mkdir("static/file/upload/dataset/single")
os.mkdir("static/file/upload/dataset/gabung")
os.mkdir("static/file/upload/sesi")

f = open("inisialisasi.sql", "r")
sintak = f.read()
try:
    mycursor.execute(sintak)
except:
    print()
finally:
    print("DONE, cek database")
    print("10 tabel")
    print("jumlah data 0,0,0,6,8,6,0,2,6,2")
# print(sintak)