import os
import time
import pymysql

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from mylib import check_photo, create_connection

app=Flask(__name__)
app.config['UPLOAD_FOLDER']='./static/photos'

app.secret_key="super secret key"

@app.route("/",methods=["GET","POST"])
def home():
    return render_template("home.html")

@app.route("/search",methods=["GET","POST"])
def search():
    if(request.method=="POST"):
        medicine_name=request.form["T1"]
        cur=create_connection()
        sql="select * from search_medicine where medicine_name LIKE '%"+medicine_name+"%'"
        cur.execute(sql)
        a=cur.rowcount
        if(a>0):
            data=cur.fetchall()
            return render_template("search.html",data=data,nm=medicine_name)
        else:
            return render_template("search.html",msg="No medicine Found")
    else:
        return render_template("search.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if(request.method=="POST"):
        email=request.form["T1"]
        password=request.form["T2"]

        cur=create_connection()

        s1="select * from logindata where email='"+email+"' AND password='"+password+"'"

        cur.execute(s1)
        a=cur.rowcount
        if(a==1):
            data=cur.fetchone()
            #fetch usertype
            ut=data[2]
            #create session
            session["email"]=email
            session["usertype"]=ut
            #send to authorization page
            if(ut=="admin"):
                return redirect(url_for("admin_home"))
            elif(ut=="medical"):
                return redirect(url_for("medical_home"))
            else:
                return render_template("login.html",msg="Usertype  does not exist. Contact to admin")
        else:
            return render_template("login.html",msg="Either email or password is incorrect")
    else:
        return render_template("login.html")
@app.route("/admin_home",methods=['GET','POST'])
def admin_home():
    if('usertype' in session):
        ut=session['usertype']
        email=session['email']`
        if(ut=="admin"):

            cur=create_connection()
            sql="select * from "
            photo=check_photo(email)

            return render_template("admin_home.html",email=email,photo=photo)

        else:
            return redirect(url_for("auth_error"))
    else:
        return  redirect(url_for("auth_error"))

@app.route("/adminphoto",methods=["GET","POST"])
def adminphoto():
    if('usertype' in session):
        ut=session['usertype']
        email=session['email']
        if(ut=='admin'):
            if(request.method=="POST"):
                file=request.files['F1']
                if file:
                    path=os.path.basename(file.filename)
                    file_ext=os.path.splitext(path)[1][1:]
                    filename=str(int(time.time())) +'.'+ file_ext
                    filename=secure_filename(filename)
                    cur=create_connection()
                    sql="insert into photodata values ('"+email+"','"+filename+"')"

                    try:
                        cur.execute(sql)
                        n=cur.rowcount
                        if(n==1):
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                            return render_template('photoupload_admin.html',result="success")
                        else:
                            return render_template('photoupload_admin.html',result="failure")
                    except:
                        return render_template('photoupload_admin.html',result="duplicate")
            else:
                return redirect(url_for("admin_home"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/changephoto_admin",methods=["GET","POST"])
def changephoto_admin():
    if('usertype' in session):
        ut=session['usertype']
        email=session['email']
        if(ut=='admin'):
            photo=check_photo(email)
            cur=create_connection()
            s1="delete from photodata where email='"+email+"'"

            cur.execute(s1)
            n=cur.rowcount
            if(n>0):
                os.remove("./static/photos/"+photo)
                return render_template("changephoto_admin.html",data="success")
            else:
                return render_template("changephoto_admin.html",data="failure")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medical_home")
def medical_home():
    if ('usertype' in session):
        ut = session['usertype']
        email=session['email']
        if (ut == "medical"):
            photo=check_photo(email)
            return render_template("medical_home.html",email=email,photo=photo)
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medicalphoto",methods=["GET","POST"])
def medicalphoto():
    if('usertype' in session):
        ut=session['usertype']
        email=session['email']
        if(ut=='admin'):
            if(request.method=="POST"):
                file=request.files['F1']
                if(file):
                    path=os.path.basename(file.filename)
                    file_ext=os.path.splitext(path)[1][1:]
                    filename=str(int(time.time())) +'.'+ file_ext
                    filename=secure_filename(filename)
                    cur=create_connection()
                    s1="insert into photodata values('"+email+"','"+filename+"')"
                    try:
                        cur.execute(s1)
                        n=cur.rowcount

                        if(n==1):
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                            return  render_template("photoupload_medical.html",result="success")
                        else:
                            return render_template("photoupload_medical.html",result="failure")
                    except:
                        return render_template("photoupload_medical.html",result="Duplicate")
            else:
                return redirect(url_for("medical_home"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for('auth_error'))

@app.route("/changephoto_medical",methods=["GET","POST"])
def changephoto_medical():
    if('usertype' in session):
        ut=session['usertype']
        email=session['email']
        if(ut=='admin'):
            photo=check_photo(email)
            cur=create_connection()
            s1="delete  from photodata where  email='"+email+"'"
            cur.execute(s1)
            n=cur.rowcount
            if(n>0):
                os.remove("./static/photos/"+photo)
                return render_template('changephoto_medical.html',data="success")
            else:
                return render_template("changephoto_medical.html",data="failure")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/logout")
def logout():
    if 'usertype' in session:
        session.pop("usertype",None)
        session.pop("email",None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route("/auth_error")
def auth_error():
    return render_template("auth_error.html")

@app.route("/medical_reg",methods=["GET","POST"])
def medical_reg():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='admin'):
            if(request.method=="POST"):
                name=request.form["T1"]
                owner=request.form["T2"]
                lno=request.form["T3"]
                address=request.form["T4"]
                contact=request.form["T5"]
                email=request.form["T6"]
                password=request.form["T7"]
                cpassword=request.form["T8"]
                usertype="medical"

                msg=""
                if(password!=cpassword):
                    msg="Password does not matched with cpassword"
                else:
                    try:
                        cur=create_connection()

                        s1="insert into medicaldata values('"+name+"','"+owner+"','"+lno+"','"+address+"','"+contact+"','"+email+"')"
                        s2="insert into logindata values('"+email+"','"+password+"','"+usertype+"')"

                        cur.execute(s1)
                        a=cur.rowcount

                        cur.execute(s2)
                        b=cur.rowcount
                        if(a==1 and b==1):
                            msg="Data is saved and login is created"
                        elif(a==1):
                            msg="Only data is saved"
                        elif(b==1):
                            msg="Only login is created"
                        else:
                            msg="NO DATA IS SAVED AND NO LOGIN IS CREATED"

                    except pymysql.err.IntegrityError:
                        msg="Email address already exist"
                return render_template("medical_reg.html", vansh=msg)
            else:
                return render_template("medical_reg.html")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/show_medicals",methods=["GET","POST"])
def show_medicals():
    cur = create_connection()

    s1 = "select * from medicaldata"

    cur.execute(s1)
    a = cur.rowcount
    if (a > 0):
        data = cur.fetchall()
        a = []
        for d in data:
            ee = d[5]  # fetch email
            photo = check_photo(ee)
            b = [d[0], d[1], d[2], d[3], d[4], ee, photo]
            a.append(b)
        return render_template("show_medical.html", vansh=a)
    else:
        return render_template("show_medical.html", msg="No Data Found")


@app.route("/edit_medical",methods=["GET","POST"])
def edit_medical():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='admin'):
            if(request.method=="POST"):
                email=request.form["H1"]
                cur=create_connection()

                s1="select * from medicaldata where email='"+email+"'"


                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    data=cur.fetchone()
                    return render_template("edit_medical.html",vansh=data)
                else:
                    return render_template("edit_medical.html",msg="No data found")
            else:
                return redirect(url_for("show_medical"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/edit_medical_1",methods=["GET","POST"])
def edit_medical_1():
    if ('usertype' in session):
        ut = session['usertype']
        e1 = session['email']
        if (ut == 'admin'):
            if(request.method=="POST"):
                name=request.form["T1"]
                owner=request.form["T2"]
                lno=request.form["T3"]
                address=request.form["T4"]
                contact=request.form["T5"]
                email=request.form["T6"]

                cur=create_connection()

                s1="update medicaldata set name='"+name+"',owner='"+owner+"',lno='"+lno+"',address='"+address+"',contact='"+contact+"' where email='"+email+"'"


                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    return  render_template("edit_medical_1.html",msg="Data changes are saved")
                else:
                    return render_template("edit_medical_1.html",msg="Data changes are not saved")

            else:
                return redirect(url_for("show_medicals"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_medical",methods=["GET","POST"])
def delete_medical():
    if ('usertype' in session):
        ut = session['usertype']
        e1 = session['email']
        if (ut == 'admin'):
            if(request.method=="POST"):
                email=request.form["H1"]

                cur=create_connection()

                s1="select * from medicaldata where email='"+email+"'"


                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    data=cur.fetchone()
                    return render_template("delete_medical.html",vansh=data)
                else:
                    return render_template("delete_medical.html",msg="No data found")
            else:
                return redirect(url_for("show_medicals"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_medical_1",methods=["GET","POST"])
def delete_medical_1():
    if ('usertype' in session):
        ut = session['usertype']
        e1 = session['email']
        if (ut == 'admin'):
            if(request.method=="POST"):
                name=request.form["T1"]
                owner=request.form["T2"]
                lno=request.form["T3"]
                address=request.form["T4"]
                contact=request.form["T5"]
                email=request.form["T6"]

                cur=create_connection()

                s1="delete from medicaldata where email='"+email+"'"


                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    return render_template("delete_medical_1.html",msg="Data changes are saved")
                else:
                    return render_template("delete_medical_1.html",msg="Data changes are not saved")
            else:
                return redirect(url_for("show_medicals"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))


@app.route("/changepass_admin",methods=["GET","POST"])
def changepass_admin():
    if ('usertype' in session):
        ut = session['usertype']
        e1=session["email"]
        if (ut == "admin"):
            if (request.method == "POST"):
                old_password = request.form["T1"]
                new_password = request.form["T2"]
                confirm_password = request.form["T3"]

                msg = ""
                if (new_password != confirm_password):
                    msg = "password does not match"
                else:

                    cur=create_connection()
                    s1 = "update logindata set password='" + new_password + "' where email='" +e1 +"' and password='"+old_password+"'"
                    cur.execute(s1)
                    n=cur.rowcount
                    if(n==1):
                        msg="Password changed successfully"
                    else:
                        msg="Invalid old password"
                    return render_template("changepass_admin.html",msg=msg)
            else:
                return render_template("changepass_admin.html")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/changepass_medical",methods=["GET","POST"])
def changepass_medical():
    if('usertype' in session):
        ut=session['usertype']
        e2=session['email']
        if(ut=="medical"):
            if(request.method=="POST"):
                old_password=request.form["T1"]
                new_password=request.form["T2"]
                confirm_password=request.form["T3"]

                msg=""
                if(new_password!=confirm_password):
                    msg="password does not matched"
                else:
                    cur=create_connection()

                    s1="update logindata set password='"+new_password+"' where email='"+e2+"' and password='"+old_password+"'"

                    cur.execute(s1)
                    a=cur.rowcount
                    if(a==1):
                        msg="password changed successfully"
                    else:
                        msg = "Invalid old password"
                    return render_template("changepass_medical.html", msg=msg)
            else:
                return render_template("changepass_medical.html")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medical_profile",methods=["GET","POST"])
def medical_profile():
    if ('usertype' in session):
        ut = session['usertype']
        e2 = session['email']
        if (ut == "medical"):

            cur=create_connection()

            if (request.method == "POST"):
                name = request.form["T1"]
                owner = request.form["T2"]
                lno = request.form["T3"]
                address = request.form["T4"]
                contact = request.form["T5"]

                cur=create_connection()

                s1 = "update medicaldata set name='" + name + "',owner='" + owner + "',lno='" + lno + "',address='" + address + "',contact='" + contact + "' where email='" + e2 + "'"



                cur.execute(s1)
                a = cur.rowcount
                if (a > 0):
                    return render_template("medical_profile.html", msg="Data changes are saved")
                else:
                    return render_template("medical_profile.html", msg="Data changes are not saved")

            else:

                sql="select * from medicaldata where email='"+e2+"'"
                cur.execute(sql)
                n=cur.rowcount
                if(n==1):
                    data=cur.fetchone()
                    return render_template("medical_profile.html",data=data)
                else:
                    return render_template("medical_profile.html",msg="No profile")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/admin_profile",methods=["GET","POST"])
def admin_profile():
    if('usertype' in session):
        ut=session['usertype']
        e2=session['email']
        if(ut=="admin"):
            cur=create_connection()

            if(request.method=="POST"):
                name=request.form["T1"]
                owner=request.form["T2"]
                lno=request.form["T3"]
                address=request.form["T4"]
                contact=request.form["T5"]

                cur=create_connection()

                s1="update medicaldata set name='"+name+"',owner='"+owner+"',lno='"+lno+"',address='"+address+"',contact='"+contact+"' where email='"+e2+"'"

                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    return render_template("admin_profile.html",msg="Data changes are saved")
                else:
                    return render_template("admin_profile.html",msg="Data changes are not saved")
            else:
                s2="select * from medicaldata where email='"+e2+"'"

                cur.execute(s2)
                b=cur.rowcount
                if(b==1):
                    data=cur.fetchone()
                    return render_template("admin_profile.html",data=data)
                else:

                    return render_template("admin_profile.html",msg="No Data Found")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medicine_add",methods=["GET","POST"])
def medicine_add():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='medical'):
            if(request.method=="POST"):
                medicine_name = request.form["T1"]
                company_name=request.form["T2"]
                licence_no=request.form["T3"]
                type_of_medicine=request.form["T4"]
                price=request.form["T5"]

                cur=create_connection()
                s1="insert into medicine_data values(0,'"+medicine_name+"','"+company_name+"','"+licence_no+"','"+type_of_medicine+"','"+price+"','"+e1+"')"

                cur.execute(s1)
                a=cur.rowcount
                if(a==1):
                    msg="Save"
                else:
                    msg="Not Saved"
                return render_template("medicine_add.html",vansh=msg)
            else:
                return render_template("medicine_add.html")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/show_medicine",methods=["GET","POST"])
def show_medicine():
    if('usertype' in session):
        ut=session["usertype"]
        e1=session["email"]
        if(ut=="medical"):

            cur=create_connection()
            s1 = "select * from medicine_data where email_medical='"+e1+"'"


            cur.execute(s1)
            a = cur.rowcount
            if (a > 0):
                data = cur.fetchall()
                return render_template("show_medicine.html", vansh=data)
            else:
                return render_template("show_medicine.html", msg="No Data Found")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/edit_medicine",methods=["GET","POST"])
def edit_medicine():
    if('usertype' in session):
        ut=session["usertype"]
        e1=session["email"]
        if(ut=="medical"):
            if(request.method=="POST"):
                medicine_id=request.form["H1"]

                cur=create_connection()

                s1="select * from medicine_data where medicine_id="+medicine_id

                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    data=cur.fetchone()
                    return render_template("edit_medicine.html",vansh=data)
                else:
                    return render_template("edit_medicine.html",msg="No data found")
            else:
                return redirect(url_for("show_medicine"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/edit_medicine_1",methods=["GET","POST"])
def edit_medicine_1():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='medical'):
            if(request.method=="POST"):
                medicine_name=request.form["T2"]
                company_name=request.form["T3"]
                licence_no=request.form["T4"]
                type_of_medicine=request.form["T5"]
                price=request.form["T6"]

                cur=create_connection()


                s1 = "update medicine_data set medicine_name='" + medicine_name + "',company_name='" + company_name + "',licence_no='" + licence_no + "',type_of_medicine='" + type_of_medicine + "',price='" + price + "' where email_medical='" + e1 + "'"

                cur.execute(s1)
                a = cur.rowcount
                if (a > 0):
                    return render_template("edit_medicine_1.html", msg="Data changes are saved")
                else:
                    return render_template("edit_medicine_1.html", msg="Data changes are not saved")

            else:
                return redirect(url_for("show_medicine"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_medicine",methods=["GET","POST"])
def delete_medicine():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='medical'):
            if(request.method=="POST"):
                medicine_id=request.form["H1"]

                cur=create_connection()
                s1="select * from medicine_data where medicine_id='"+medicine_id+"'"

                cur.execute(s1)
                a=cur.rowcount

                if(a>0):
                    data=cur.fetchone()
                    return render_template("delete_medicine.html",vansh=data)
                else:
                    return render_template("delete_medicine.html",msg="NO Data found")
            else:
                return redirect("show_medicine")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/delete_medicine_1",methods=["GET","POST"])
def delete_medicine_1():
    if('usertype' in session):
        ut=session["usertype"]
        e1=session["email"]
        if(ut=='medical'):
            if(request.method=="POST"):
                medicine_id=request.form["T1"]
                medicine_name=request.form["T2"]
                company_name=request.form["T3"]

                licence_no=request.form["T4"]
                type_of_medicine=request.form["T5"]
                price=request.form["T6"]

                cur=create_connection()
                s1="delete from medicine_data where medicine_id='"+medicine_id+"' "

                cur.execute(s1)
                a=cur.rowcount
                if(a>0):
                    return render_template("delete_medicine_1.html",msg="Data changes are saved successfully")
                else:
                    return render_template("delete_medicine_1.html",msg="Data changes are not saved successfully")

            else:
                return redirect(url_for("show_medicine"))
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))

@app.route("/medical_photo",methods=["GET","POST"])
def medical_photo():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='admin'):
            file=request.files["F1"]
            e1=request.form["H1"]
            if(file):
                path=os.path.basename(file.filename)
                file_ext=os.path.splitext(path)[1][1:]
                filename=str(int(time.time())) +'.'+ file_ext
                filename=secure_filename(filename)

                cur=create_connection()
                s1="insert into photodata values('"+e1+"','"+filename+"')"
                try:
                    cur.execute(s1)
                    n=cur.rowcount
                    if(n==1):
                        file.save(os.path.join("./static/photos",filename))
                        return render_template("medical_photo.html",result="success")
                    else:
                        return render_template("medical_photo.html",result="failure")
                except:
                    return render_template("medical_photo.html",result="duplicate")
            else:
                return render_template("show_medicals.html")
        else:
            return redirect(url_for("auth_error"))
    else:

        return redirect(url_for("auth_error"))

@app.route("/change_medical_photo",methods=["GET","POST"])
def change_medical_photo():
    if('usertype' in session):
        ut=session['usertype']
        e1=session['email']
        if(ut=='admin'):
            if(request.method=="POST"):
                e1=request.form['H1']
                photo=request.form['H2']

                cur=create_connection()
                s1="update photodata set photo='no' where email='"+e1+"'"
                s2="delete from photodata where email='"+e1+"'"
                cur.execute(s1)
                n=cur.rowcount
                cur.execute(s2)
                b=cur.rowcount
                if(n>0 and b>0):
                    os.remove("./static/photos/" +photo)
                    return render_template("change_medical_photo.html",result="success")
                else:
                    return render_template("change_medical_photo.html",result="failure")
            else:
                return render_template("show_medicals")
        else:
            return redirect(url_for("auth_error"))
    else:
        return redirect(url_for("auth_error"))


if(__name__=="__main__"):
    app.run(debug=True)