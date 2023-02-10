from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from user import User
from flask_bcrypt import  Bcrypt;
import re
from flask_app import app


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "bananas"

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
PMT_REGEX = re.compile(r"^\d*[.,]?\d*$")



@app.route('/')
def index():
    
    users = User.all_users()
    print(users)
    return render_template("index.html", users=users)  

# REGISTRATION PAGE AND REGISTRATION SUBMIT
@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/submit', methods=['POST'])
def submit():
    session.clear()
    print("ENTERED SUBMIT ROUTE")
    is_valid = True

    print(request.form['email'])
    print(request.form['first_name'])
    print(request.form['last_name'])
    print(request.form['username'])
    print(request.form['password'])
    userquery = "SELECT * FROM users"
    existingUsers = connectToMySQL("ezbingo").query_db(userquery)
    for one in existingUsers: #   EMAIL VALIDATION
        if one['email'] == request.form['email'].lower():
            is_valid = False
            flash("email is already taken", "email")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!")
    for one in existingUsers: #   USERNAME VALIDATION
        if one['username'] == request.form['username'].lower():
            is_valid = False
            flash("that username is already taken", "username")
    if len(request.form['first_name']) < 2: # NAME VALIDATION
        is_valid = False
        flash("Please enter a first name", "firstname")
    if not NAME_REGEX.match(request.form['first_name']):
        is_valid = False
        flash("Name can only include letters", "firstname")
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("Please enter a last name")
    if not NAME_REGEX.match(request.form['last_name']):
        is_valid = False
        flash("name can only include letters")
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Please enter a password with at least 8 characters") #PASSWORD VALIDATION
    if (request.form['password'] != request.form['confirm_password']):
        is_valid = False
        flash("Passwords DO NOT Match")
    print(is_valid)
    if not is_valid:
        return redirect ('/register')
    
    else:
        flash("Registration Successful!", "register")
        hashedPass = bcrypt.generate_password_hash(request.form['password'])
        
        data = {
            'first_name' : request.form['first_name'],
            'last_name' : request.form['last_name'],
            'email' : request.form['email'].lower(),
            'password' : hashedPass,
            'username': request.form['username'].lower(),
            }
        query = "INSERT INTO users (first_name, last_name, username, email, password, created_at, updated_at) VALUES (%(first_name)s,%(last_name)s, %(username)s, %(email)s, %(password)s,NOW(),NOW());"
        users = connectToMySQL("ezbingo").query_db(query, data)
        print(users)
        
        return redirect ('/')

if __name__== "__main__":
    app.run(debug=True)