import os
from flask import Flask, render_template, url_for, redirect, session, request, flash
import re
from datetime import *
import ibm_db

from mailjet_rest import Client

app = Flask(__name__)

#mailjet
api_key = 'e40c383c11bccb2164a329ceb5ab0427'
api_secret = 'b991822038153f622b0aa0ae8ce20d4f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

conn = ibm_db.connect("DATABASE=bludb;  HOSTNAME=815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30376;  SECURITY=SSL;  SSLServerCertificate=DigiCertGlobalRootCA.crt;  UID=tbx03863;  PWD=zYmHIpR01SXSL2YV", '', '')

@app.route('/')
def index():
    return render_template('index.html')

#----------------------------NORMAL USER ROUTES-----------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    global userid
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT * FROM users WHERE username=? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['USERNAME']
            userid = account['USERNAME']
            session['username'] = account['USERNAME']
            return render_template('dashboard.html', msg=username)
        else:
            msg = "Invalid login credentials!"
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = "Please fill out the form."
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = "Username already exists!"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email address!"
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = "Username must contain only letters and numbers!"
        else:
            insertsql = "INSERT INTO users VALUES(?,?,?)"
            prepstmt = ibm_db.prepare(conn, insertsql)
            ibm_db.bind_param(prepstmt, 1, username)
            ibm_db.bind_param(prepstmt, 2, email)
            ibm_db.bind_param(prepstmt, 3, password)
            ibm_db.execute(prepstmt)

            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": "19i209@psgtech.ac.in",
                            "Name": "Darshan"
                        },
                        "To": [
                        {
                            "Email": email,
                            "Name": username
                        }
                    ],
                        "Subject": "Registration Verification.",
                        "TextPart": "Congratulations! Welcome new user!",
                        "HTMLPart": "<h1>Plasma App Registration Verification</h1>''<p>Congratulations! Welcome new user</p>''<br><br>''<b>Plasma Donor App Team</b>!</p>!",
                    }
                ]
            }
            result = mailjet.send.create(data=data)
            
            msg = "You have successfully created an account!"
            flash(msg)
            return redirect(url_for('index'))    
    return render_template('register.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', msg=userid)

@app.route('/newdonor')
def newdonor():
    username = userid
    sql = "SELECT username FROM donor WHERE username=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print("reached account", account)
    if account:
        msg = "You have already registered as a donor! Donor registration is only 1 time!"
        flash(msg)
        return redirect(url_for('dashboard'))
    return render_template('newdonor.html')

@app.route('/newrequest')
def newrequest():
    return render_template('newrequest.html')

@app.route('/regdonor', methods=['GET', 'POST'])
def regdonor():
    msg = ""
    if request.method == "POST":
        username = userid
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phno = request.form['phone']
        addr = request.form['address']
        city = request.form['city']
        state = request.form['state']
        bgp = request.form['bloodgp']
        don = request.form['don']
        if int(age)<18:
            msg="You have to be an adult to donate plasma!"

        else:
            insertsql = "INSERT INTO donor VALUES(?,?,?,?,?,?,?,?,?,?)"
            prepstmt = ibm_db.prepare(conn, insertsql)
            ibm_db.bind_param(prepstmt, 1, username)
            ibm_db.bind_param(prepstmt, 2, name)
            ibm_db.bind_param(prepstmt, 3, age)
            ibm_db.bind_param(prepstmt, 4, gender)
            ibm_db.bind_param(prepstmt, 5, phno)
            ibm_db.bind_param(prepstmt, 6, addr)
            ibm_db.bind_param(prepstmt, 7, city)
            ibm_db.bind_param(prepstmt, 8, state)
            ibm_db.bind_param(prepstmt, 9, bgp)
            ibm_db.bind_param(prepstmt, 10, don)
            ibm_db.execute(prepstmt)
            msg = "You have successfully applied as a donor."
            print("executed insert")
            
    flash(msg)
    return redirect(url_for('dashboard'))

@app.route('/regrequest', methods=['GET', 'POST'])
def regrequest():
    msg = ""
    if request.method == "POST":
        username = userid
        pname = request.form['pname']
        print(userid, "\t", session['id'], "pname = ", pname)
        sql = "SELECT * FROM requests WHERE username=? AND pname=?" #patient's name = pname
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, pname)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print("reached account here for pname", account)
        if account:
            msg = "Register for a patient only once!"
            flash(msg)
            return redirect(url_for('dashboard'))
        
        phno = request.form['phone']
        paddr = request.form['paddress']
        city = request.form['city']
        state = request.form['state']
        bgp = request.form['bloodgp']

        insertsql = "INSERT INTO requests VALUES(?,?,?,?,?,?,?)"
        prepstmt = ibm_db.prepare(conn, insertsql)
        ibm_db.bind_param(prepstmt, 1, username)
        ibm_db.bind_param(prepstmt, 2, pname)
        ibm_db.bind_param(prepstmt, 3, phno)
        ibm_db.bind_param(prepstmt, 4, paddr)
        ibm_db.bind_param(prepstmt, 5, city)
        ibm_db.bind_param(prepstmt, 6, state)
        ibm_db.bind_param(prepstmt, 7, bgp)
        print("prep insert - "+username+"--"+pname+"--"+bgp)
        ibm_db.execute(prepstmt)
        msg = "You have successfully requested plasma."
        print("executed insert")        
    flash(msg)
    return redirect(url_for('dashboard'))

@app.route('/pastrequests')
def pastrequests():
    username = userid
    flag = 0
    data = []
    sql = "SELECT pname,phone,paddress,city,state,blood FROM requests WHERE username=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    request = ibm_db.fetch_tuple(stmt)
    while request != False:
        flag = 1 #atleast 1 match is found
        data.append(request)
        request = ibm_db.fetch_tuple(stmt)
    if not flag:
        msg = "You have made 0 requests!"
        flash(msg)
        return redirect(url_for('dashboard'))
    else:
        print("No of requests = ", len(data))
        data = tuple(data)
        headings = ("Patient's Name", "Emergency Contact", "Patient's Address", "City", "State", "Blood Group Requested", "Options")
        return render_template('userrequests.html', msg=userid, data=data, headings=headings)

@app.route('/adminrequests')
def adminrequests():
    username = userid
    sql = "SELECT blood FROM donor WHERE username=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    mybgp = ibm_db.fetch_tuple(stmt)
    print("My bgp is: ", mybgp)
    if not mybgp:
        msg = "You have not registered as a donor yet! Please register first to view other's requests!"
        flash(msg)
        return redirect(url_for('dashboard'))
    
    flag = 0
    data = []
    sql = "SELECT pname,phone,state,blood FROM approved WHERE blood=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, mybgp[0])
    ibm_db.execute(stmt)
    request = ibm_db.fetch_tuple(stmt)
    while request != False:
        flag = 1 #atleast 1 match is found
        data.append(request)
        request = ibm_db.fetch_tuple(stmt)
    if not flag:
        print("My bgp is: ", mybgp)
        msg = "No requests for your blood group were found!"
        flash(msg)
        return redirect(url_for('dashboard'))
    else:
        print("No of mybgp requests = ", len(data))
        data = tuple(data)
        headings = ("Patient's Name", "Emergency Contact", "State", "Blood Group Requested")
        return render_template('bgprequests.html', msg=userid, data=data, headings=headings)

@app.route('/profile')
def profile():
    username = userid
    dictprofile = {'Username':'', 'Email ID': '', 'Is Donor?': 'NO'}
    dictprofile['Username'] = username

    sql = "SELECT email FROM users WHERE username=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    dictprofile['Email ID'] = ibm_db.fetch_tuple(stmt)[0]
    
    sql = "SELECT * FROM donor WHERE username=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.execute(stmt)
    gotprofile = ibm_db.fetch_tuple(stmt)
    if gotprofile:
        dictprofile['Is Donor?'] = 'YES'
        dictprofile['Full Name'] = gotprofile[1]
        dictprofile['Age'] = gotprofile[2]
        dictprofile['Gender'] = gotprofile[3]
        dictprofile['Phone Number'] = gotprofile[4]
        dictprofile['Address'] = gotprofile[5]
        dictprofile['City'] = gotprofile[6]
        dictprofile['State'] = gotprofile[7]
        dictprofile['Blood Group'] = gotprofile[8]
        dictprofile['Date of Negative Covid Test'] = gotprofile[9]
    return render_template('userprofile.html', msg=userid, dictprofile = dictprofile)
    


#----------------------------ADMIN ROUTES-----------------------------------

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    global adminid
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT * FROM admins WHERE username=? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['USERNAME']
            adminid = account['USERNAME']
            session['username'] = account['USERNAME']
            return redirect(url_for('admindashboard'))
        else:
            msg = "Invalid admin credentials!"
    return render_template('adminlogin.html', msg=msg)

@app.route('/admindashboard')
def admindashboard():
    sql = "SELECT COUNT(*) FROM requests"
    stmt = ibm_db.exec_immediate(conn, sql)
    numreqs = ibm_db.fetch_tuple(stmt)[0]
    
    sql = "SELECT COUNT(*) FROM donor"
    stmt = ibm_db.exec_immediate(conn, sql)
    numdonors = ibm_db.fetch_tuple(stmt)[0]

    sql = "SELECT COUNT(*) FROM approved"
    stmt = ibm_db.exec_immediate(conn, sql)
    numappreqs = ibm_db.fetch_tuple(stmt)[0]

    if not numreqs: numreqs = 0
    if not numappreqs: numappreqs = 0
    if not numdonors: numdonors = 0

    print(numreqs, numdonors, numappreqs)
    return render_template('admindashboard.html', msg=adminid, numreqs=numreqs, numdonors=numdonors, numappreqs=numappreqs)

@app.route('/allrequests')
def allrequests():
    data = []
    flag = 0
    sql = "SELECT * FROM requests"
    stmt = ibm_db.exec_immediate(conn, sql)
    request = ibm_db.fetch_tuple(stmt)
    while request != False:
        flag = 1 #atleast 1 match is found
        data.append(request)
        request = ibm_db.fetch_tuple(stmt)
    if not flag:
        msg = "There are 0 requests!"
        flash(msg)
        return redirect(url_for('admindashboard'))
    else:
        print("No of requests = ", len(data))
        data = tuple(data)
        headings = ("Username", "Patient's Name", "Emergency Contact", "Patient's Address", "City", "State", "Blood Group Requested", "Options")
        return render_template('viewallreqs.html', msg=adminid, data=data, headings=headings)

@app.route('/approvereq', methods=['POST','GET'])
def approvereq():
    if request.method == "POST":
        bgp = request.form["bgp"]
        print("Request approved for bgp = ", bgp)

        pname = request.form['pname']
        phno = request.form['phone']
        state  = request.form['state']

        sql = "SELECT * FROM approved WHERE pname=? AND blood=? AND phone=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, pname)
        ibm_db.bind_param(stmt, 2, bgp)
        ibm_db.bind_param(stmt, 3, phno)
        ibm_db.execute(stmt)
        appreq = ibm_db.fetch_assoc(stmt)
        print("reached appreq", appreq)
        if appreq:
            msg = "Request already approved! Approve only 1 time!"
            flash(msg)
            return redirect(url_for('admindashboard'))
        
        insertsql = "INSERT INTO approved VALUES(?,?,?,?)"
        prepstmt = ibm_db.prepare(conn, insertsql)
        ibm_db.bind_param(prepstmt, 1, pname)
        ibm_db.bind_param(prepstmt, 2, phno)
        ibm_db.bind_param(prepstmt, 3, state)
        ibm_db.bind_param(prepstmt, 4, bgp)
        ibm_db.execute(prepstmt)
        msg = "You have successfully approved a request."
        print("executed insert")        
    flash(msg)
    return redirect(url_for('admindashboard'))

@app.route('/alldonors')
def alldonors():
    data = []
    flag = 0
    sql = "SELECT * FROM donor"
    stmt = ibm_db.exec_immediate(conn, sql)
    donor = ibm_db.fetch_tuple(stmt)
    while donor != False:
        flag = 1 #atleast 1 match is found
        data.append(donor)
        donor = ibm_db.fetch_tuple(stmt)
    if not flag:
        msg = "There are 0 donors!"
        flash(msg)
        return redirect(url_for('admindashboard'))
    else:
        print("No of donors = ", len(data))
        data = tuple(data)
        headings = ("Username", "Full Name", "Age", "Gender", "Phone Number", "Donor's Address", "City", "State", "Blood Group", "-ve Covid Test")
        return render_template('viewalldonors.html', msg=adminid, data=data, headings=headings)


#----------------------------GENERAL LOGOUT ROUTES-----------------------------------

@app.route('/deletereq', methods=['GET','POST'])
def deletereq():
    if request.method == 'POST':
        username = request.form['username']
        pname = request.form['pname']
        delsql = "DELETE FROM requests WHERE username=? AND pname=?"
        prepstmt = ibm_db.prepare(conn, delsql)
        ibm_db.bind_param(prepstmt, 1, username)
        ibm_db.bind_param(prepstmt, 2, pname)
        ibm_db.execute(prepstmt)
        msg = "You have successfully deleted the request."
        print("executed delete: ", pname)
        flash(msg)
        if 'adminid' in globals():
            return redirect(url_for('admindashboard'))
        elif 'userid' in globals():
            return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('Loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    if 'userid' in globals():
        global userid
        del userid
    elif 'adminid' in globals():
        global adminid
        del adminid
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)