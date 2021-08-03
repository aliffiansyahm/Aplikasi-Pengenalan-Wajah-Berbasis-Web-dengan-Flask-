from flask import (
    Flask, render_template, request, session,
    url_for, redirect,flash,abort ,Response)
import time
import shutil
import json
from werkzeug.utils import secure_filename
import os
from os import path
from capture_interval import capture_utama,capture_single
from dbConnect import koneksi
from camera import VideoCamera
import hashlib
import threading
from proses import proses_hasil_capture
from gabungGambar import gabung
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretKEYS"
db = koneksi()
mycursor = db.cursor()

app.config['UPLOAD_SINGLE_PHOTO_FOLDER'] = 'static\\file\\upload\\dataset\\single'
app.config['UPLOAD_DATABASE_PHOTO_FOLDER'] = 'static\\file\\upload\\dataset'

@app.errorhandler(401)
def unout(e):
    return render_template('401.html'),401
@app.route('/')
def index():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route("/login",methods=["GET","POST"])
def login():
    if 'email_login' in session:
        return redirect(url_for('dashboard'))
    else:
        if request.method == "POST":
            if request.form['password'] == '':
                abort(401)
            email = request.form['email']
            password = request.form['password']
            hashedPassword = hashlib.md5("pw-{}".format(password).encode('utf-8')).hexdigest()
            mycursor.execute("SELECT p.id_pengguna,tp.nama_tipe_pengguna "
                "FROM pengguna as p, tipe_pengguna as tp "
                "where p.email_pengguna = '" + email + "' "
                "and p.password_pengguna = '" + hashedPassword +"' "
                "and p.id_tipe_pengguna = tp.id_tipe_pengguna")
            data = mycursor.fetchall()
            if len(data) == 1:
                session['id_pengguna'] = data[0][0]
                session['email_login'] = email
                session['tipe_login'] = data[0][1]
                flash("Selamat datang "+email,'success')
                return redirect(url_for('dashboard'))
            else :
                flash("Detail salah",'danger')
                return render_template('login.html')
        else:
            return render_template('login.html')

@app.route('/logout')
def logout():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'email_login' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

# PENGGUNA
@app.route('/list_pengguna')
def list_pengguna():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM pengguna")
    data = mycursor.fetchall()
    return render_template('pengguna/index.html',value = data)

@app.route('/buat_pengguna',methods=["GET","POST"])
def buat_pengguna():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        if request.form['password'] == '':
            abort(401)
        email = request.form['email']
        password = request.form['password']
        hashedPassword = hashlib.md5("pw-{}".format(password).encode('utf-8')).hexdigest()

        mycursor.execute("select email_pengguna from pengguna where email_pengguna = '"+email+"'")
        data = mycursor.fetchall()
        if len(data) == 0:
            mycursor.execute("insert into pengguna "
                "values ( '','2', '" + email + "' , '" + hashedPassword + " ' )")
            db.commit()
            flash("Berhasil menambahkan  "+email,'success')
        else:
            flash("email  "+email+" sudah ada",'danger')

        return redirect(url_for('list_pengguna'))
    else:
        return render_template('pengguna/buat.html')

@app.route('/ganti_password',methods=["GET","POST"])
def ganti_password():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM pengguna where id_pengguna = '"+ str(session['id_pengguna']) +"'")
    data = mycursor.fetchall()
    if request.method == "POST":
        if request.form['password_lama'] == '' or request.form['password_baru1'] == '' or request.form['password_baru2'] == '':
            abort(401)
        passwordLama = request.form['password_lama']
        hashedPasswordLama = hashlib.md5("pw-{}".format(passwordLama).encode('utf-8')).hexdigest()
        if hashedPasswordLama != data[0][3]:
            flash("Password lama salah",'danger')
            return redirect(url_for('ganti_password'))
        if request.form['password_baru1'] != request.form['password_baru2']:
            flash("Password baru tidak sama",'danger')
            return redirect(url_for('ganti_password'))
        password = request.form['password_baru1']
        hashedPassword = hashlib.md5("pw-{}".format(password).encode('utf-8')).hexdigest()
        mycursor.execute("update pengguna "
            "set password_pengguna = '" + hashedPassword + "'" +
            "where id_pengguna = '" + str(session['id_pengguna']) + "'")
        db.commit()
        flash("Berhasil merubah password",'success')
        return redirect(url_for('dashboard'))
    return render_template('gantiPassword.html')

@app.route('/edit_pengguna/<id_pengguna>',methods=["GET","POST"])
def edit_pengguna(id_pengguna):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM pengguna where id_pengguna = '"+ id_pengguna +"'")
    data = mycursor.fetchall()
    if request.method == "POST":
        if request.form['password'] == '':
            abort(401)
        email = request.form['email']
        password = request.form['password']
        hashedPassword = hashlib.md5("pw-{}".format(password).encode('utf-8')).hexdigest()

        mycursor.execute("update pengguna "
            "set  email_pengguna = '"+ email + "' ,password_pengguna = '" + hashedPassword + "'" +
            "where id_pengguna = '" + id_pengguna + "'")
        db.commit()
        flash("Berhasil mengedit  "+email,'success')
        return redirect(url_for('list_pengguna'))
    return render_template('pengguna/edit.html',data=data)

@app.route('/hapus_pengguna/<id_pengguna>')
def hapus_pengguna(id_pengguna):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM pengguna where id_pengguna = '"+ id_pengguna +"'")
    data = mycursor.fetchall()
    if len(data) == 1:
        mycursor.execute("delete "
                "FROM pengguna where id_pengguna = '"+ id_pengguna +"'")
        db.commit()
        flash("Berhasil menghapus",'success')
        return redirect(url_for('list_pengguna'))
    else:
        flash("data yang di hapus tidak ada",'error')
        return redirect(url_for('list_pengguna'))

# mata_kuliah
@app.route('/list_mata_kuliah')
def list_mata_kuliah():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM mata_kuliah")
    data = mycursor.fetchall()
    return render_template('mata_kuliah/index.html',value = data)

@app.route('/buat_mata_kuliah',methods=["GET","POST"])
def buat_mata_kuliah():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        if request.form['mata_kuliah'] == '':
            abort(401)
        mata_kuliah = request.form['mata_kuliah']
        mycursor.execute("insert into mata_kuliah "
            "values ( '','" + mata_kuliah + "')")
        db.commit()
        flash("Berhasil menambahkan",'success')
        return redirect(url_for('list_mata_kuliah'))
    else:
        return render_template('mata_kuliah/buat.html')

@app.route('/edit_mata_kuliah/<id_mata_kuliah>',methods=["GET","POST"])
def edit_mata_kuliah(id_mata_kuliah):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM mata_kuliah where id_mata_kuliah = '"+ id_mata_kuliah +"'")
    data = mycursor.fetchall()
    if request.method == "POST":
        if request.form['mata_kuliah'] == '':
            abort(401)
        mata_kuliah = request.form['mata_kuliah']
        mycursor.execute("update mata_kuliah "
            "set  nama_mata_kuliah = '"+ mata_kuliah + "'" +
            "where id_mata_kuliah = '" + id_mata_kuliah + "'")
        db.commit()
        flash("Berhasil mengedit  "+mata_kuliah,'success')
        return redirect(url_for('list_mata_kuliah'))
    return render_template('mata_kuliah/edit.html',data=data)

@app.route('/hapus_mata_kuliah/<id_mata_kuliah>')
def hapus_mata_kuliah(id_mata_kuliah):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM mata_kuliah where id_mata_kuliah = '"+ id_mata_kuliah +"'")
    data = mycursor.fetchall()
    if len(data) == 1:
        mycursor.execute("delete "
                "FROM mata_kuliah where id_mata_kuliah = '"+ id_mata_kuliah +"'")
        db.commit()
        flash("Berhasil menghapus",'success')
        return redirect(url_for('list_mata_kuliah'))
    else:
        flash("data yang di hapus tidak ada",'error')
        return redirect(url_for('list_mata_kuliah'))

# kelas
@app.route('/list_kelas')
def list_kelas():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT k.id_kelas,sk.nama_status_kelas,k.nama_kelas "
                "FROM kelas as k, status_kelas as sk "
                "where k.id_status_kelas=sk.id_status_kelas order by k.nama_kelas")
    data = mycursor.fetchall()
    return render_template('kelas/index.html',value = data)

@app.route('/cek_kelas/<id_kelas>')
def cek_kelas(id_kelas):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    session["nilai_id_kelas"] = id_kelas
    mycursor.execute("SELECT * "
                "FROM mahasiswa where id_kelas = '"+ id_kelas +"' order by nrp_mahasiswa")
    data = mycursor.fetchall()
    siap = False
    mycursor.execute("SELECT * "
                    "FROM kelas where id_kelas = '"+ session['nilai_id_kelas'] +"'")
    kelas = mycursor.fetchone()
    nama_kelas = kelas[2]
    if len(data) > 0 :
        siap = True
        for mhs in data:
            if mhs[4] == '':
                # print(mhs[4])
                siap = False
        
        if siap:
            mycursor.execute("UPDATE kelas SET id_status_kelas='2' WHERE id_kelas='"+session['nilai_id_kelas']+"'")
            flash("Berhasil merubah status {} menjadi Siap".format(nama_kelas),'success')
            db.commit()
        else:
            flash("Kelas {} belum siap. Lengkapi foto nya".format(nama_kelas),'error')
    else:
        flash("Kelas {} belum siap. Belum ada murid ".format(nama_kelas),'error')
    return redirect(url_for('list_kelas'))


@app.route('/buat_template/<id_kelas>')
def buat_template(id_kelas):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ id_kelas +"'")
    data = mycursor.fetchone()
    kelas = data[2]
    asal = os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],kelas)
    tujuan = os.path.join(app.config['UPLOAD_DATABASE_PHOTO_FOLDER'],'gabung')
    gabung(asal,tujuan,kelas)
    flash("Perhasil Membuar template kelas {}".format(kelas),'success')
    return redirect(url_for('list_kelas')) 

@app.route('/buat_kelas',methods=["GET","POST"])
def buat_kelas():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        if request.form['kelas'] == '':
            abort(401)
        kelas = request.form['kelas']
        mycursor.execute("insert into kelas "
            "values ( '','1','" + kelas + "')")
        db.commit()
        flash("Berhasil menambahkan",'success')
        return redirect(url_for('list_kelas'))
    else:
        return render_template('kelas/buat.html')

@app.route('/edit_kelas/<id_kelas>',methods=["GET","POST"])
def edit_kelas(id_kelas):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ id_kelas +"'")
    data = mycursor.fetchall()
    if request.method == "POST":
        if request.form['kelas'] == '':
            abort(401)
        kelas = request.form['kelas']
        mycursor.execute("update kelas "
            "set  nama_kelas = '"+ kelas + "'" +
            "where id_kelas = '" + id_kelas + "'")
        db.commit()
        flash("Berhasil edit  "+kelas,'success')
        return redirect(url_for('list_kelas'))
    return render_template('kelas/edit.html',data=data)

@app.route('/hapus_kelas/<id_kelas>')
def hapus_kelas(id_kelas):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ id_kelas +"'")
    data = mycursor.fetchall()
    folder_kelas = data[0][2]
    if len(data) == 1:
        mycursor.execute("delete "
                "FROM kelas where id_kelas = '"+ id_kelas +"'")
        db.commit()
        flash("Berhasil menghapus",'success')
        try:
            shutil.rmtree(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas))
            shutil.rmtree(os.path.join(app.config['UPLOAD_DATABASE_PHOTO_FOLDER'],'gabung',folder_kelas))
        except:
            pass
        return redirect(url_for('list_kelas'))
    else:
        flash("data yang di hapus tidak ada",'error')
        return redirect(url_for('list_kelas'))

@app.route('/lihat_kelas/<id_kelas>',methods=["GET","POST"])
def lihat_kelas(id_kelas):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    session["nilai_id_kelas"] = id_kelas
    mycursor.execute("SELECT * "
                "FROM mahasiswa where id_kelas = '"+ id_kelas +"' order by nrp_mahasiswa")
    data = mycursor.fetchall()
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ id_kelas +"'")
    kelas = mycursor.fetchone()
    return render_template('mahasiswa/index.html',data_mhs=data,kelas=kelas)

ALLOWED_EXTENSION = set(['png','jpg','jpeg'])
def allowed_file(filename):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION

#mahasiswa
@app.route('/buat_mahasiswa',methods=["GET","POST"])
def buat_mahasiswa():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ session['nilai_id_kelas'] +"'")
    data = mycursor.fetchone()
    folder_kelas = data[2]
    
    if request.method == "POST":
        if request.form['nrp'] == '' or request.form['nama'] == '':
            abort(401)
        nrp = request.form['nrp']
        nama = request.form['nama']

        file = request.files['file']
        kosong = True
        filename = ''
        if 'file' not in request.files:
            pass
           
        if file.filename not in request.files:
            pass            

        if file and allowed_file(file.filename):
            if not path.exists(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas)):
                os.mkdir(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas))
            filename = nrp + "-" + nama + ".jpg"
            kosong = False
            file.save(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas,filename))
        if kosong:
             mycursor.execute("insert into mahasiswa "
            "values ( '','"+session["nilai_id_kelas"]+"','" + nrp + "','"+nama+"','')")
        else:
             mycursor.execute("insert into mahasiswa "
            "values ( '','"+session["nilai_id_kelas"]+"','" + nrp + "','"+nama+"','"+filename+"')")
            
        mycursor.execute("UPDATE kelas SET id_status_kelas='1' WHERE id_kelas='"+session['nilai_id_kelas']+"'")
        db.commit()
        flash("Berhasil menambahkan",'success')
        return redirect(url_for('lihat_kelas',id_kelas=session["nilai_id_kelas"]))
    else:
        return render_template('mahasiswa/buat.html')

@app.route('/edit_mahasiswa/<id_mahasiswa>',methods=["GET","POST"])
def edit_mahasiswa(id_mahasiswa):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ session['nilai_id_kelas'] +"'")
    data = mycursor.fetchone()
    folder_kelas = data[2]
    mycursor.execute("SELECT * "
                "FROM mahasiswa where id_mahasiswa = '"+ id_mahasiswa +"'")
    data = mycursor.fetchall()
    if request.method == "POST":
        if request.form['nrp'] == '' or request.form['nama'] == '':
            abort(401)
        nrp = request.form['nrp']
        nama = request.form['nama']
        file = request.files['file']
        kosong = True
        filename = ''
        if 'file' not in request.files:
            pass
        if file.filename not in request.files:
            pass            
        if file and allowed_file(file.filename):
            if not path.exists(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas)):
                os.mkdir(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas))
            filename = filename = nrp + "-" + nama + ".jpg"
            kosong = False
            if data[0][4] != '':
                os.remove(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas,data[0][4]))
            file.save(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas,filename))
        else:
            flash('data tersimpan namun gambar tidak dapat di simpan. pilih gambar lain')
        if kosong:
            mycursor.execute("update mahasiswa "
            "set  nama_mahasiswa = '"+ nama + "',nrp_mahasiswa = '" + nrp +"'"+ 
            "where id_mahasiswa = '" + id_mahasiswa + "'")
        else:
            mycursor.execute("update mahasiswa "
            "set  nama_mahasiswa = '"+ nama + "',nrp_mahasiswa = '" + nrp +"'"+ ",foto_mahasiswa = '"+filename+"' " 
            "where id_mahasiswa = '" + id_mahasiswa + "'")
        mycursor.execute("UPDATE kelas SET id_status_kelas='1' WHERE id_kelas='"+session['nilai_id_kelas']+"'")
        db.commit()
        flash("Berhasil mengubah "+nama,'success')
        return redirect(url_for('lihat_kelas',id_kelas=session["nilai_id_kelas"]))
    return render_template('mahasiswa/edit.html',data=data)

@app.route('/lihat_mahasiswa/<id_mahasiswa>',methods=["GET","POST"])
def lihat_mahasiswa(id_mahasiswa):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT k.nama_kelas,m.nrp_mahasiswa,m.nama_mahasiswa ,m.foto_mahasiswa "
                "FROM mahasiswa as m,kelas as k where m.id_mahasiswa = '"+ id_mahasiswa +"' and k.id_kelas = m.id_kelas")
    data = mycursor.fetchone()
    pathFoto = ''
    if data[3] == '':
        pathFoto = 'static\\no-pic.png'
    else:
        pathFoto = os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],data[0],data[3])
    return render_template('mahasiswa/lihat.html',data=data,pathFoto=pathFoto)

@app.route('/hapus_mahasiswa/<id_mahasiswa>')
def hapus_mahasiswa(id_mahasiswa):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM kelas where id_kelas = '"+ session['nilai_id_kelas'] +"'")
    data = mycursor.fetchone()
    folder_kelas = data[2]
    mycursor.execute("SELECT * "
                "FROM mahasiswa where id_mahasiswa = '"+ id_mahasiswa +"'")
    data = mycursor.fetchall()
    mycursor.execute("UPDATE kelas SET id_status_kelas='1' WHERE id_kelas='"+session['nilai_id_kelas']+"'")
    if len(data) == 1:
        mycursor.execute("delete "
                "FROM mahasiswa where id_mahasiswa = '"+ id_mahasiswa +"'")
        try:
            os.remove(os.path.join(app.config['UPLOAD_SINGLE_PHOTO_FOLDER'],folder_kelas,data[0][4]))
        except:
            pass
        db.commit()
        flash("Berhasil menghapus",'success')
        return redirect(url_for('lihat_kelas',id_kelas=session["nilai_id_kelas"]))
    else:
        flash("data yang di hapus tidak ada",'error')
        return redirect(url_for('lihat_kelas',id_kelas=session["nilai_id_kelas"]))

#ruang
@app.route('/list_ruang')
def list_ruang():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM ruang")
    data = mycursor.fetchall()
    return render_template('ruang/index.html',value=data)

@app.route('/buat_ruang',methods=["GET","POST"])
def buat_ruang():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        if request.form['alamat'] == '' or request.form['ruang'] == '':
            abort(401)
        alamat = request.form['alamat']
        ruang = request.form['ruang']
        mycursor.execute("insert into ruang "
            "values ( '','"+ruang+"','" + alamat + "')")
        db.commit()
        flash("Berhasil menambahkan",'success')
        return redirect(url_for('list_ruang'))
    else: 
        return render_template('ruang/buat.html')
@app.route('/edit_ruang/<id_ruang>',methods=["GET","POST"])
def edit_ruang(id_ruang):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM ruang where id_ruang = '"+ id_ruang +"'")
    data = mycursor.fetchall()

    if request.method == "POST":
        if request.form['alamat'] == '' or request.form['ruang'] == '':
            abort(401)
        alamat = request.form['alamat']
        ruang = request.form['ruang']
        mycursor.execute("update ruang "
            "set  nama_ruang = '"+ ruang + "',alamat_kamera = '" + alamat +"' "+ 
            "where id_ruang = '" + id_ruang + "'")
        db.commit()
        flash("Berhasil mengubah "+ruang,'success')
        return redirect(url_for('list_ruang'))
    return render_template('ruang/edit.html',data=data)

@app.route('/hapus_ruang/<id_ruang>')
def hapus_ruang(id_ruang):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM ruang where id_ruang = '"+ id_ruang +"'")
    data = mycursor.fetchall()
    if len(data) == 1:
        mycursor.execute("delete "
                "FROM ruang where id_ruang = '"+ id_ruang +"'")
        db.commit()
        flash("Berhasil menghapus",'success')
        return redirect(url_for('list_ruang'))
    else:
        flash("data yang di hapus tidak ada",'error')
        return redirect(url_for('list_ruang'))

#sesi
@app.route('/list_sesi')
def list_sesi():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT s.id_sesi,k.nama_kelas,mk.nama_mata_kuliah,ss.nama_status_sesi, "
                "s.nama_sesi, s.waktu_mulai_sesi,r.nama_ruang,r.alamat_kamera "
                "FROM sesi as s,status_sesi as ss,mata_kuliah as mk,kelas as k,ruang as r "
                "where s.id_pengguna = '"+ str(session['id_pengguna']) +"' and "
                "s.id_status_sesi = ss.id_status_sesi and "
                "s.id_mata_kuliah_fk = mk.id_mata_kuliah and "
                "s.id_kelas = k.id_kelas and "
                "s.id_ruang = r.id_ruang "
                "order by s.waktu_mulai_sesi desc")
    data = mycursor.fetchall()
    return render_template('sesi/index.html',value=data)
from datetime import datetime
@app.route('/buat_sesi',methods=["GET","POST"])
def buat_sesi():
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("select * "
                "from mata_kuliah")
    mata_kuliah = mycursor.fetchall()
    mycursor.execute("select k.id_kelas, k.nama_kelas "
                "from kelas as k, status_kelas as sk "
                "where k.id_status_kelas = sk.id_status_kelas "
                "and sk.nama_status_kelas = 'Siap' "
                "order by k.nama_kelas")
    kelas = mycursor.fetchall()
    mycursor.execute("select * "
                "from ruang")
    ruang = mycursor.fetchall()

    if request.method == "POST":
        if request.form['ruang'] == '':
            abort(401)
        id_mata_kuliah_fk = request.form['mata_kuliah']
        id_kelas = request.form['kelas']
        id_pengguna = session['id_pengguna']
        ruang = request.form['ruang']
        mycursor.execute("select nama_kelas from kelas where id_kelas = '"+id_kelas+"'")
        nama_kelas = mycursor.fetchone()
        mycursor.execute("select nama_mata_kuliah from mata_kuliah where id_mata_kuliah = '"+id_mata_kuliah_fk+"'")
        nama_mata_kuliah = mycursor.fetchone()
        now = datetime.now()
        current_time = now.strftime("%d-%m-%Y %H-%M-%S")
        nama_sesi = "{}_{}_{}".format(nama_kelas[0],nama_mata_kuliah[0],current_time)
        mycursor.execute("INSERT INTO `sesi` (`id_sesi`, `id_mata_kuliah_fk`, `id_pengguna`, `id_status_sesi`, `id_kelas`, `nama_sesi`, `waktu_mulai_sesi`, `id_ruang`) "
                "VALUES (NULL, '"+str(id_mata_kuliah_fk)+"', '"+str(id_pengguna)+"', '1', '"+str(id_kelas)+"', '"+nama_sesi+"', NULL, '"+ruang+"')")

        db.commit()
        flash("Berhasil membuat sesi untuk {} pada mata kuliah {} pada {}".format(nama_kelas,nama_mata_kuliah,current_time),'success')
        threading.Thread(target=penutup_sesi,kwargs=dict(nama_sesi=nama_sesi)).start()
        
        return redirect(url_for('list_sesi'))
    else:
        return render_template('sesi/buat.html',kelas=kelas,mata_kuliah=mata_kuliah,ruang=ruang)

@app.route('/lihat_sesi/<id_sesi>')
def lihat_sesi(id_sesi):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("select id_sesi,nama_sesi from sesi where id_sesi = '"+id_sesi+"'")
    sesi = mycursor.fetchone()
    record_path = 'static/file/record/'+sesi[1]
    if os.path.exists(record_path) and os.path.isdir(record_path):
        filelist = os.listdir(record_path)
        filename = filelist[0]
        filepath = os.path.join(record_path,filename)
        with open(filepath) as json_file:
            data = json.load(json_file)
        i = 0
        for mhs in data['Absensi']:
            mycursor.execute("select nama_mahasiswa from mahasiswa where nrp_mahasiswa = '"+mhs['NRP']+"'")
            namaMHS = mycursor.fetchone()
            data['Absensi'][i]['Nama'] = namaMHS[0]
            i += 1
        return render_template('sesi/lihat.html',data=data)
    else:
        flash("Belum ada Data harap tunggu",'error')
        return redirect(url_for('list_sesi'))
    # return "in developmend"

@app.route('/edit_sesi/')
def edit_sesi():
    return "in developmend"

@app.route('/hapus_sesi/<id_sesi>')
def hapus_sesi(id_sesi):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM sesi where id_sesi = '"+ id_sesi +"'")
    data = mycursor.fetchall()
    if len(data) == 1:
        dirpath = 'static/file/proses/capturan/'+data[0][5]
        try:
            shutil.rmtree(dirpath)
        except Exception:
            pass
        mycursor.execute("delete from sesi where id_sesi = '"+id_sesi+"'")
        db.commit()
        flash("Berhasil menghapus",'success')
        return redirect(url_for('list_sesi'))
    else:
        flash("data yang di hapus tidak ada",'error')
        return redirect(url_for('list_pengguna'))
    db.commit()

@app.route('/mulai_capture/<id_sesi>')
def mulai_capture(id_sesi):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("select s.id_sesi,s.nama_sesi,r.alamat_kamera,k.nama_kelas "
                "from sesi as s,kelas as k,ruang as r where s.id_kelas = k.id_kelas and s.id_ruang = r.id_ruang and s.id_sesi ='"+id_sesi+"'")
    sesi = mycursor.fetchone()
    mycursor.execute("update sesi set id_status_sesi = '2' "
                "where id_sesi ='"+id_sesi+"'")
    db.commit()
    threading.Thread(target=task,kwargs=dict(nama_sesi=sesi[1],ip=sesi[2],kelas=sesi[3])).start()
    flash("Berhasil memulai Capturing {}".format(sesi[1]))
    return redirect(url_for('list_sesi'))

@app.route('/mulai_capture_manual/<id_sesi>')
def mulai_capture_manual(id_sesi):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("select s.id_sesi,s.nama_sesi,r.alamat_kamera,k.nama_kelas,s.id_ruang "
                "from sesi as s,kelas as k,ruang as r where s.id_kelas = k.id_kelas and s.id_ruang = r.id_ruang and s.id_sesi ='"+id_sesi+"'")
    sesi = mycursor.fetchone()
    
    mycursor.execute("SELECT * "
                "FROM ruang where id_ruang = '"+ str(sesi[4]) +"'")
    kelas = mycursor.fetchone()
    # return render_template('cetak.html',data=dataa)
    # return kelas;
    return render_template('sesi/manual_capture.html',ipcam = kelas[2][:-6],sesi=sesi)

@app.route('/cap_man/<id_sesi>')
def cap_man(id_sesi):
    print("cap_man")
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("select s.id_sesi,s.nama_sesi,r.alamat_kamera,k.nama_kelas "
                "from sesi as s,kelas as k,ruang as r where s.id_kelas = k.id_kelas and s.id_ruang = r.id_ruang and s.id_sesi ='"+id_sesi+"'")
    sesi = mycursor.fetchone()
    mycursor.execute("update sesi set id_status_sesi = '2' "
                "where id_sesi ='"+id_sesi+"'")
    db.commit()
    threading.Thread(target=task2,kwargs=dict(nama_sesi=sesi[1],ip=sesi[2],kelas=sesi[3])).start()
    print('sini')
    return redirect(url_for('list_sesi'))

@app.route('/tutup_sesi/<id_sesi>')
def tutup_sesi(id_sesi):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    status = simpan_db(id_sesi)
    if status == 1:
        flash("berhasil meyimpan absensi {}".format(id_sesi),'success')
    elif status == 2:
        flash("Belum ada file",'error')
    else:
        flash('sesi sudah di tutup')
    return redirect(url_for('list_sesi'))

def simpan_db(id_sesi):
    mycursor.execute("select id_sesi,nama_sesi from sesi where id_status_sesi = '5' and id_sesi = '"+id_sesi+"'")
    sesi = mycursor.fetchall()
    if len(sesi) == 0:
        mycursor.execute("select id_sesi,nama_sesi from sesi where id_sesi = '"+id_sesi+"'")
        sesi = mycursor.fetchone()
        record_path = 'static/file/record/'+sesi[1]
        if os.path.exists(record_path) and os.path.isdir(record_path):
            filelist = os.listdir(record_path)
            filename = filelist[0]
            filepath = os.path.join(record_path,filename)
            baca_record_insert_db(id_sesi,filepath)
            mycursor.execute("update sesi set id_status_sesi = '5' "
                    "where id_sesi ='"+id_sesi+"'")
            db.commit()
            return 1
        else:
            return 2
    else:
        return 3

def baca_record_insert_db(id_sesi,filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)

    i = 0
    command_insert = "INSERT INTO absensi (id_absensi, id_sesi_fk, id_mahasiswa_fk, waktu) VALUES "
    for x in data["Absensi"]:
        mycursor.execute("SELECT * FROM mahasiswa WHERE nrp_mahasiswa="+x['NRP'])
        MHS = mycursor.fetchone()
        # print(listMHS)
        # print(sesi[0])
        # print(MHS[0])
        tanggal = x['tanggal'][-4:] + x['tanggal'][2:6] + x['tanggal'][:2]
        waktu = tanggal + " " + x['waktu']
        row = "( NULL , '" + str(id_sesi) +"','" + str(MHS[0]) +"','" + waktu + "'),"
        i=i+1
        command_insert = command_insert + row

    command_insert = command_insert[0:-1] + ";"
    mycursor.execute(command_insert)
    db.commit()
    print(mycursor.rowcount, "record inserted.")

#video
@app.route('/cek_kamera/<id_ruang>')
def cek_kamera(id_ruang):
    if 'email_login' not in session:
        return redirect(url_for('login'))
    mycursor.execute("SELECT * "
                "FROM ruang where id_ruang = '"+ id_ruang +"'")
    kelas = mycursor.fetchone()
    return render_template('video.html',ipcam = kelas[2][:-6],namaRuang=kelas[1])

@app.route('/video/<id_sesi>')
def video(id_sesi):
    mycursor.execute("select r.alamat_kamera, r.nama_ruang "
                    "from sesi as s,ruang as r "
                    " where s.id_sesi = '"+id_sesi+"' and "
                    " s.id_ruang = r.id_ruang")
    sesi = mycursor.fetchone()
    # return sesi[0]
    return render_template('video.html',ipcam = sesi[0][:-6],namaRuang=sesi[1])

def gen(camera):
    while True:
        data = camera.get_frame()
        frame = data[0]
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.route('/video_feed/<string:ip>')
def video_feed(ip):
    # alamat = 'http://192.168.1.11:8080/video'
    alamat = 'http://'+ip+'/video'
    return Response(gen(VideoCamera(alamat)),mimetype='multipart/x-mixed-replace; boundary=frame')


def task(nama_sesi,ip,kelas):
    print("masuk tread")
    print(threading.current_thread().name)
    print("memulai capture {}".format(nama_sesi))
    capture_utama(nama_sesi,ip)
    print('capture selesai mulai mengenali')
    mycursor.execute("update sesi set id_status_sesi = '3' "
                "where nama_sesi ='"+nama_sesi+"'")
    print("Masukkan gambar sekarang ke folder {}".format(nama_sesi))
    time.sleep(20)
    print("stop masukkan gambar test")
    db.commit()
    proses_hasil_capture(nama_sesi,kelas)
    mycursor.execute("update sesi set id_status_sesi = '4' "
                "where nama_sesi ='"+nama_sesi+"'")
    db.commit()
    print("keluar tread")

def task2(nama_sesi,ip,kelas):
    print("masuk tread capture manual")
    print(threading.current_thread().name)
    print("memulai capture {}".format(nama_sesi))
    capture_single(nama_sesi, ip)
    print('capture selesai mulai mengenali')
    mycursor.execute("update sesi set id_status_sesi = '3' "
                "where nama_sesi ='"+nama_sesi+"'")
    db.commit()
    proses_hasil_capture(nama_sesi,kelas)
    mycursor.execute("update sesi set id_status_sesi = '4' "
                "where nama_sesi ='"+nama_sesi+"'")
    db.commit()
    print("keluar tread")

def penutup_sesi(nama_sesi):
    print("------------------Menutup sesi otomatis dimulai--------------")
    #waktu otomatis terturup setelah sesi di buat
    time.sleep(300)
    print("Menutup sesi otomatis di tutup")
    waiting = True
    while waiting:
        print("menunggu proses mengenali")
        mycursor.execute("select id_sesi,id_status_sesi from sesi "
            "where nama_sesi ='"+nama_sesi+"'")
        data = mycursor.fetchone()
        print("{} <> {}".format(data[1],type(data[1])))
        if data[1] == 4:
            # print ("masuk sini")
            status = simpan_db(str(data[0]))
            waiting = False
        elif data[1] == 5:
            waiting = False
        else:
            pass
        time.sleep(30)

if __name__ == '__main__':
    app.run(debug=True,host='192.168.1.11')