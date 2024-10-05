#set light and dark themes
#set official email for reset token
#handls before request 
#change route names to avoid #unauthorized entry

from flask import Flask,request, render_template, session, redirect, url_for
import sqlite3
from os import environ
from secrets import token_urlsafe
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def getConn():
  conn = sqlite3.connect('database.db')
  return conn

def getCon():
  conn = sqlite3.connect('account.db')
  return conn
  
def reset_token():
  tok = token_urlsafe(16)
  return tok

conn = getCon()
pointer = conn.cursor()
pointer.execute("CREATE TABLE IF NOT EXISTS accounts(email Text, name TEXT, account_number TEXT, leverage TEXT, account_type TEXT, password Text, balance Text)")
#pointer.execute("Insert into accounts #values('oqibz@example.com', 'John #Doe', '1234567890', '1:1000', #'Real','zitegeist','30')")

conn.commit()
conn.close()



con = getConn()
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT, password TEXT, country TEXT, reset Text)")

con.commit()
con.close()



app = Flask(__name__)
app.secret_key = environ.get("Secret_Key")
if not app.secret_key:
  app.secret_key = token_urlsafe(32)

@app.route("/")
def hello():
  return render_template("login.html")

@app.route("/account")
def account():

  conn = getCon()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM accounts")
  account = cursor.fetchall()
  conn.close()
  
  return render_template("account.html", account=account, theme="blac")

@app.route("/signup")
def signup():
  return render_template("signup.html")
@app.route("/reset")
def reset():
  return render_template("reset.html")
  
@app.route("/login")
def login():
  return render_template("login.html")

@app.route("/loginDetail", methods=["POST"])
def loginDetail():
  if request.method == "POST":
    email = request.form["email"].strip()
    password = request.form["password"]
    con = getConn()
    cursor = con.cursor()
    cursor.execute("SELECT password from users Where email = :email", {"email": email})
    data = cursor.fetchone()
    print(data)
    if data and data[0] == password:
      con.close()
      session['email'] = email
      return redirect(url_for("account"))
      
    else:
      con.close()
      return "Wrong email or password", 400
      
@app.route("/newPassword", methods=["POST", "GET"])
def newPassword():
  if request.method == "POST":
    password = request.form["password"]
    
    con = getConn()
    cursor = con.cursor()
    cursor.execute("Update users set password = :password where email = :email", {'password':password, 'email':session['email']})
    con.commit()
    con.close()
    session.pop('token', None)
    session.pop('email', None)
    return redirect(url_for("login"))
  elif request.method == "GET":
    return render_template("New_password.html")

  
@app.route("/resetToken", methods=["POST", "GET"])
def resetToken():
  token = session['token']
  if request.method == "POST":
    return redirect(url_for("newPassword"))
  return render_template("resetToken.html", token=token)
      
@app.route("/resetEmailDetail", methods= ["POST"])
def resetEmailDetail():
  email = request.form["email"]
  token = reset_token()
  con = getConn()
  cursor = con.cursor()
  cursor.execute("Update users set reset = :token Where email = :email", {"email": email, "token": token})
  con.commit()
  con.close()
  session['email'] = email
  session['token'] = token
  sender_email = "officialtutspot@gmail.com"
  sender_password = "nuhu gkud kyud fgae"
  recipient_email = email
  body = f"Your password reset token is {session['token']}"
  subject = 'Password Reset'
  message = MIMEMultipart()
  message["From"] = "Tutspot.net"
  message["To"] = recipient_email
  message["Subject"] = subject
  message.attach(MIMEText(body, "plain"))
  try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, message.as_string())
    server.quit()
    print("Email sent successfully!")
  except Exception as e:
    print(f"Failed to send email: {e}")
  return redirect(url_for("resetToken"))
         
  
    
@app.route("/signupDetail", methods=["GET", "POST"])
def signupDetail():

  if request.method == "POST":
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    password = request.form["password"].strip()
    country = request.form["country"].strip()
    con = getConn()
    cursor = con.cursor()
    cursor.execute("Select email from users where email = :email", {"email": email})
    data = cursor.fetchone()
  
    print(data)
    if data and email in data[0]:
      con.close()
      return "Email already exists", 400
        
    else:
      cursor.execute("INSERT INTO users VALUES(:name, :email, :password, :country, '00000')", {'name':name, 'email':email, 'password':password, 'country':country})
      con.commit()
      con.close()
      return redirect(url_for("account"))

if __name__ == "__main__":
  app.run(debug=True)