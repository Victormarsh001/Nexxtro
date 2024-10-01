from flask import Flask,request, render_template
import sqlite3


def getConn():
  conn = sqlite3.connect('database.db')
  return conn
  
con = getConn()
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT, password TEXT, country TEXT)")

con.commit()
con.close()



app = Flask(__name__)

@app.route("/")
def hello():
  return render_template("home.html")

@app.route("/signup")
def signup():
  return render_template("signup.html")

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