from flask import session
from mysqlconnection import connectToMySQL
class Validation:
    @classmethod
    def validate_user(user):
        is_valid = True
        coolquery = "SELECT * FROM users"
        db_list = connectToMySQL("ezbingo").query_db(coolquery)
        for one in db_list:
            if one['email'] == request.form['email']:
                if request.form['email'] == session['email']:
                    break
                is_valid = False
                flash("email is already taken",)
        if len(request.form['first_name']) < 2:
            is_valid = False
            flash("**Please enter a first name**")
        if not NAME_REGEX.match(request.form['first_name']):
            is_valid = False
            flash("Name can only include letters")
        if len(request.form['last_name']) < 2:
            is_valid = False
            flash("Please enter a last name", "lastname")
        if not NAME_REGEX.match(request.form['last_name']):
            is_valid = False
            flash("name can only include letters")
        if not EMAIL_REGEX.match(request.form['email']):
            is_valid = False
            flash("Invalid email address!")

        return is_valid