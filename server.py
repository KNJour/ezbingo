from flask import Flask, render_template, request, redirect, session, flash, Response, make_response, send_file
from mysqlconnection import connectToMySQL
from user import User
import random
from flask_bcrypt import  Bcrypt;
import re
import pdfkit
from flask_app import app
import spot
# Importing reportlab library for pdf generation


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


# VALIDATIONS & LOGIN ----------------------------------
# Validation for Login User
@app.route('/login', methods=['POST'])
def login():
    data = {
        'username' : request.form['username'].lower()
    }
    hashedpassword = request.form['password']
    print(request.form['username'].lower())
    print(hashedpassword)
    # FIRST, checks to see if field put in 'username' login box is an email or not. if it does not match email regex it queries users. if it does it queries emails. 
    if not EMAIL_REGEX.match(request.form['username']):
        print('KNOWS IT ISNT EMAIL')
        userquery = "SELECT * FROM users WHERE username = %(username)s"
        user = connectToMySQL("ezbingo").query_db(userquery, data)

        if len(user) < 1:
            flash("no username or email found", "login")
            return redirect('/')
        if user:
            if bcrypt.check_password_hash(user[0]["password"], hashedpassword): #stores info in session
                session['first_name'] = user[0]["first_name"]
                session['last_name'] = user[0]["last_name"]
                session['username'] = user[0]["username"]
                session['user_id'] = user[0]["id"]
                session['email'] = user[0]['email']
                return redirect('/dashboard')
            else:
                print ("THE ELSE PASSWORD BAD")
                flash("password is incorrect", "login")
                return redirect('/')
    else: 
        emailquery = "SELECT * FROM users WHERE email = %(username)s"
        user = connectToMySQL("ezbingo").query_db(emailquery, data)
        if len(user) < 1:
            flash("no username or email found", "login")
            return redirect('/')
        if bcrypt.check_password_hash(user[0]["password"], hashedpassword):
            session['first_name'] = user[0]["first_name"]
            session['last_name'] = user[0]["last_name"]
            session['username'] = user[0]["username"]
            session['user_id'] = user[0]["id"]
            session['email'] = user[0]['email']
            return redirect('/dashboard')
        else:
            print ("THE ELSE")
            flash("password is incorrect", "login")
            return redirect('/')
        

# LOGOUT - CLEARS SESSION AND LOGS OUT TO INDEX
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
# DASHBOARD ------------------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        print("NOT IN SESSION")
        return redirect('/')

    data = {
        "user_id": session['user_id'],
    }

    playlist_query = "SELECT * FROM playlists WHERE user_id = %(user_id)s;"
    playlists = connectToMySQL('ezbingo').query_db(playlist_query, data)
    username = session['username']
    print(username)
    return render_template("dashboard.html", playlists=playlists, username = username)

# CREATING & EDITING PLAYLISTS ----------------------------------
@app.route('/playlists')
def playlists():
    if 'user_id' not in session:
        print("NOT IN SESSION")
        return redirect('/logout')
    data = {
        "user_id": session['user_id']
    }
    playlist_query = "SELECT * FROM playlists WHERE user_id = %(user_id)s;"
    playlists = connectToMySQL('ezbingo').query_db(playlist_query, data)

    return render_template("playlists.html", playlists = playlists, username = session['username'])

@app.route('/submit_playlist', methods=['GET', 'POST'])
def submit_playlist():
    if 'user_id' not in session:
        print("NOT IN SESSION")
        return redirect('/')
    if request.method == 'POST':
        data = {
            "name" : request.form['playlist_name'],
            "user_id" : session['user_id']
        }
        query = "INSERT INTO playlists (user_id, playlist_name, created_at, updated_at) VALUES (%(user_id)s, %(name)s, NOW(),NOW())"
        newPlaylist = connectToMySQL('ezbingo').query_db(query,data)

        flash("playlist successfully created!")
        return redirect ('/playlists')

# CREATING AND DELETING SONGS
@app.route('/songs', methods=['POST', 'GET'])
def songs():
    if 'user_id' not in session:
        print("NOT IN SESSION")
        return redirect('/')
    if request.method == 'POST':
        if request.form['playlist_id']:
            print("ADDING PLAYLIST ID FROM REQUEST-FORM TO SESSION")
            session['playlist_id'] = request.form['playlist_id']
            session['playlist_name'] = request.form['playlist_name']

        data = {
            "user_id" : session['user_id'],
            "playlist_id" : request.form['playlist_id']
        }

        songQuery = "SELECT * FROM songs WHERE playlist_id = %(playlist_id)s;"
        currentsongs = connectToMySQL('ezbingo').query_db(songQuery,data)
        return render_template('songs.html', currentsongs = currentsongs, playlist_name = request.form['playlist_name'], playlist_id = request.form['playlist_id'])
    if request.method == 'GET':
        print('ITS THE GET METHOD')
        data = {
            "user_id" : session['user_id'],
            "playlist_id" : session['playlist_id']
        }
        songQuery = "SELECT * FROM songs WHERE playlist_id = %(playlist_id)s;"
        currentsongs = connectToMySQL('ezbingo').query_db(songQuery,data)
        return render_template('songs.html', currentsongs = currentsongs, playlist_name = session['playlist_name'], playlist_id = session['playlist_id'])

@app.route('/create_song/', methods=['POST'])
def create_song():
    if 'user_id' not in session or 'playlist_id' not in session:
        print("NOT IN SESSION")
        return redirect('/logout')

    data = {
        "title" : request.form['title'],
        "artist" : request.form['artist'],
        "playlist_id" : session['playlist_id'],
        "user_id" : session['user_id']
    }
    query = "INSERT INTO songs (playlist_id, title, artist, created_at, updated_at) VALUES (%(playlist_id)s, %(title)s, %(artist)s, NOW(),NOW())"
    addSong = connectToMySQL('ezbingo').query_db(query,data)
    flash("song successfully created!")
    return redirect ('/songs')

@app.route('/delete_song', methods=['GET', 'POST'])
def delete_song():
    data = {
        'song_id': request.form['song_id'],
        'user_id' : session['user_id']
    }
    query = "DELETE FROM songs WHERE id = %(song_id)s;"
    delete_song = connectToMySQL('ezbingo').query_db(query,data)
    print(session['playlist_id'])
    return redirect ('/songs')

# DELETE PLAYLISTS & SONGS ---------------------------------------------
@app.route('/delete_playlist', methods=['GET', 'POST'])
def delete_playlist():
    query = "DELETE FROM playlists WHERE id = %(playlist_id)s;"
    data = {
        'playlist_id': request.form['playlist_id'],
        'user_id' : session['user_id']
    }
    
    delete_playlist = connectToMySQL('ezbingo').query_db(query,data)
    return redirect('/playlists')

# Page to create cards
@app.route('/card_settings', methods=['POST'])
def card_settings():
    session['playlist_id'] = request.form['playlist_id']
    session['playlist_name'] = request.form['playlist_name']

    # songQuery = "SELECT * FROM songs WHERE playlist_id = %(playlist_id)s;"
    # currentsongs = connectToMySQL('ezbingo').query_db(songQuery,data)
    return render_template('/card_settings.html')

@app.route('/create_cards', methods=['POST'])
def create_cards():
    data = {
            "user_id" : session['user_id'],
            "playlist_id" : session['playlist_id']
        }
    query = "SELECT * FROM songs WHERE playlist_id = %(playlist_id)s;"
    songs = connectToMySQL('ezbingo').query_db(query,data)
    playlist = []
    for song in songs:
        full_song = str(song['title'])
        if song['artist']:
            full_song = str(f'{full_song} ({song["artist"]})')
        playlist.append(full_song)
    # Gather desired settings from form
    print(playlist)
    # checks if there are enough songs (not using grid size initially) 
    # songs_required = (grid_size * grid_size) - 1
    cards_per_page = int(request.form['cards_per_page'])
    num_cards = int(request.form['num_cards'])
    # if len(playlist) < songs_required:
    #     return "Error: Playlist does not have enough unique elements to create the bingo card."
    
    options = {
    'page-size': 'Letter',
    'orientation': 'Landscape'
    }
    playlist_name = session['playlist_name']
    cards = randomize_cards(playlist, num_cards)
    rendered = render_template('template.html', cards=cards, playlist_name=playlist_name)
    pdf = pdfkit.from_string(rendered, False, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    return response


# grabs 24 songs from playlist (only 24 due to free space) for cards
def randomize_cards(playlist, num_cards):
    cards = []
    for _ in range(num_cards):
        songs = playlist.copy()  # create a copy of the playlist for each card desired
        random.shuffle(songs)  # Shuffles, duh
        cards.append(songs[:24])  # take first 24 songs for the bingo card
    return cards


#  Spotify generation route start
@app.route('/spotify')
def spotify():
    if 'user_id' not in session:
        print("NOT IN SESSION")
        return redirect('/')
    return render_template('/spotify_template.html')

@app.route('/create_spotify_playlist', methods=['POST'])
def create_spotify_playlist():

    url_list = request.form['list'].split()
    spot.convert_to_playlist(url_list, session['user_id'], request.form['playlist_name'])
    print(spot.__name__)
    return redirect('/dashboard')
if __name__== "__main__":
    app.run(debug=True)