import shutil
import cv2
from datetime import datetime
import os

pic_taken = 5
def resize(img,height):
    height = int(height)
    width = int(img.shape[1] / img.shape[0] * height)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

def simpan(name,image):
    status = cv2.imwrite(name, image)
    print(".")

def capture_utama(nama_sesi,ip):
    dirpath = 'static/file/proses/capturan/'+nama_sesi;
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H_%M_%S")
    cap = cv2.VideoCapture(0)

    cap.open("http://"+ip)
    saved = False
    i=1
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)
    saved_sec = 0
    while i <= pic_taken:
        ret,img = cap.read()
        if ret:
            img = resize(img,600)
            grayscale = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
            now = datetime.now()
            # print("->>>"+ str(saved) +"-->"+str(now.second))
            if(saved is False and now.second%5==0 and saved_sec!= now.second):
                captured_time = now.strftime("%H_%M_%S")
                filename = dirpath + '/' + str(current_time) + '___' + str(i)+'___'+captured_time+'.jpg'
                # print(filename)
                # print(i)
                i = i + 1
                saved_sec = now.second
                simpan(filename,grayscale)
                saved = True
            else:
                saved = False
            # cv2.imshow("Imagae from " + address,img)
            # key = cv2.waitKey(1)
            # if key == 27:
            #     break
    cap.release()

def capture_single(nama_sesi,ip):
    dirpath = 'static/file/proses/capturan/'+nama_sesi;
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H_%M_%S")
    cap = cv2.VideoCapture(0)

    cap.open("http://"+ip)
    saved = False
    i=1
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)
    ret,img = cap.read()
    if ret:
        img = resize(img,600)
        grayscale = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        now = datetime.now()
        captured_time = now.strftime("%H_%M_%S")
        filename = dirpath + '/' + str(current_time) + '___' + str(i)+'___'+captured_time+'.jpg'
        i = i + 1
        saved_sec = now.second
        simpan(filename,grayscale)
    cap.release()

# utama()