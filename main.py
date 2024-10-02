from flask import Flask,request, render_template, session
import sqlite3
from os import environ
from secrets import token_urlsafe
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def getConn():
  conn = sqlite3.connect('database.db')
  return conn
def reset_token():
  tok = token_urlsafe(16)
  return tok
  
con = getConn()
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT, password TEXT, country TEXT, reset Text Nullable)")

con.commit()
con.close()



app = Flask(__name__)
app.secret_key = environ.get("Secret_Key")
if not app.secret_key:
  app.secret_key = token_urlsafe(32)

@app.route("/")
def hello():
  return render_template("login.html")

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
    email = request.form["email"]
    password = request.form["password"]
    con = getConn()
    cursor = con.cursor()
    cursor.execute("SELECT password from users Where email = :email", {"email": email})
    data = cursor.fetchone()
    print(data)
    if data and data[0] == password:
      con.close()
      return "Login Success", 200
      
    else:
      con.close()
      return "Wrong email or password", 400
@app.route("/newPassword", methods=["POST"])
def newPassword():
  return "Token Match!!", 200;

  
@app.route("/resetToken")
def resetToken():
  token = session['token']
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
  body = f"Your password reset token is {token}"
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
  return redirect(url_for(resetToken))
         
  
    
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
      return "Email already exists", 404
        
    else:
      cursor.execute("INSERT INTO users VALUES(:name, :email, :password, :country)", {'name':name, 'email':email, 'password':password, 'country':country})
      con.commit()
      con.close()
      return "Success", 200;

if __name__ == "__main__":
  app.run(debug=True)