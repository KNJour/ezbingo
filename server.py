from flask import Flask, render_template, request, redirect, session, flash
from user import User
from mysqlconnection import connectToMySQL


app = Flask(__name__)
@app.route('/')
def index():
    userlist = connectToMySQL('ezbingo').query_db("SELECT * FROM users")
    print(userlist)
    print("xxxxx")
    users = User.all_users()
    print(users)
    return render_template("index.html", users = users, allusers=userlist)  


if __name__== "__main__":
    app.run(debug=True)