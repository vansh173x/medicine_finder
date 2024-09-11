import pymysql

def create_connection():
    con=pymysql.connect(host="localhost",port=3306,user="root",passwd="",db="vansh",autocommit=True)
    cur=con.cursor()
    return cur
def check_photo(email):
    cur=create_connection()
    cur.execute("select * from photodata where email='"+email+"'")
    n=cur.rowcount
    photo="no"

    if(n>0):
        row=cur.fetchone()
        photo=row[1]
    return photo
