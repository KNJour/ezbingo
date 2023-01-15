from flask import Flask, render_template, request, redirect, session, flash
from user import User
from mysqlconnection import connectToMySQL
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
    userlist = connectToMySQL('ezbingo').query_db("SELECT * FROM users")
    print(userlist)
    print("xxxxx")
    users = User.all_users()
    print(users)
    return render_template("index.html", allusers = userlist, users=users)  

# REGISTRATION PAGE AND REGISTRATION SUBMIT
@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/submit', methods=['POST'])
def submit():
    session.clear()
    is_valid = True
    userquery = "SELECT * FROM users"
    user_list = connectToMySQL("ezbingo").query_db(userquery)
    for one in user_list: #   EMAIL VALIDATION
        if one['email'] == request.form['email']:
            is_valid = False
            flash("email is already taken", "email")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!")
    for one in user_list: #   USERNAME VALIDATION
        if one['username'] == request.form['username']:
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
        return redirect ('/')
    
    else:
        flash("Registration Successful!", "register")
        hashedPass = bcrypt.generate_password_hash(request.form['password'])

        query = "INSERT INTO users (first_name, last_name, user_name, email, password, created_at, updated_at) VALUES (%(first_name)s,%(last_name)s, %(username)s, %(email)s, %(password)s,NOW(),NOW());"
        
        print(query)
        data = {
            'first_name' : request.form['first_name'],
            'last_name' : request.form['last_name'],
            'email' : request.form['email'].lower(),
            'password' : hashedPass,
            'username': request.form['username'].lower(),
            }
        users = connectToMySQL("budgets").query_db(query, data)
        print(users)
        
        return redirect ('/')

if __name__== "__main__":
    app.run(debug=True)