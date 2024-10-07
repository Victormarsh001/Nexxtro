#set light and dark themes
#set official email for reset token
#handls before request 
#change route names to avoid #unauthorized entry

from flask import Flask,request, render_template, session, redirect, url_for
import sqlite3
from datetime import datetime
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

def getPost():
  conn = sqlite3.connect('diss.db')
  return conn
  
def reset_token():
  tok = token_urlsafe(16)
  return tok

co = getPost()
posts = co.cursor()
posts.execute("CREATE TABLE IF NOT EXISTS posts(id Text, email Text, name Text, date Text, post Text)")

posts.execute("CREATE TABLE IF NOT EXISTS comments(id Text, name Text, date Text, comment Text)")

#posts.execute("Insert into comments Values(:id, :name, :date, :comment)", {'id':'1', 'name':'Victor Basy', 'date':'6/10/2021', 'comment':'You too man'})

#posts.execute("Insert into posts Values(:id, :email, :name, :date, :post)", {'id':'1', 'email':'victorbasy17.3@gmail.com', 'name':'Victor Basy', 'date':'6/10/2021', 'post':'Have a nice trading day everyone!!'})
co.commit()
co.close()


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
  return redirect(url_for("login"))

@app.route("/publisher", methods=["GET", "POST"])
def publisher():
  if request.method == "POST":
    post = request.form.get("post")
    date = datetime.now().strftime("%d/%m/%Y")
    
    conn = getPost()
    cursor = conn.cursor()
    cursor.execute("Select id from posts")
    id = len(cursor.fetchall()) + 1
    cursor.execute("Insert into posts Values(:id, :email, :name, :date, :post)", {'id':str(id), 'email':session['email'], 'name':session['name'], 'date':date, 'post':post})
    conn.commit()
    conn.close()
    return redirect(url_for("post"))
                                  
  return render_template("publisher.html")

@app.route("/comment", methods=["GET","POST"])
def comment():
  if request.method == "POST":
    id = session['commentId']
    comment = request.form.get("comments")
    date = datetime.now().strftime("%d/%m/%Y")
    name = session['name']

    conn = getPost()
    cursor = conn.cursor()
    cursor.execute("Insert into comments Values(:id, :name, :date, :comment)",{'id':id, 'name':name, 'date':date, 'comment':comment})
    conn.commit()
    conn.close()
    return redirect(url_for("commentView"))
  
  return render_template("comment.html")

@app.route("/commentView")
def commentView():
  id = request.args.get("id")
  name = request.args.get("name")

  if 'commentId' not in session or 'name'  not in session:
    session['commentId'] = id
    session['name'] = name

  
  con = getPost()
  cursor = con.cursor()
  cursor.execute("Select * from comments where id = :id", {'id':session['commentId']})
  data = cursor.fetchall()[::-1]
  con.close()
  return render_template("commentView.html", data=data, name=session['name'])


@app.route("/post")
def post():
  post = getPost()
  cursor = post.cursor()
  cursor.execute("Select * from posts")
  data = cursor.fetchall()[::-1]
  post.close()
  return render_template("post.html", data=data)


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
    cursor.execute("SELECT password, name from users Where email = :email", {"email": email})
    data = cursor.fetchone()
    print(data)
    if data and data[0] == password:
      session['name'] = data[1]
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