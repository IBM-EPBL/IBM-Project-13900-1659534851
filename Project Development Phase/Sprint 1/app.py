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