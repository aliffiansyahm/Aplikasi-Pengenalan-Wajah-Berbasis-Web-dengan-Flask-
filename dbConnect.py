import mysql.connector
def koneksi():
    mydb = mysql.connector.connect(
        host="#",
        user="#",
        password="",
        database="#"
    )
    return mydb
