from flask import Flask, render_template, request, redirect, session, flash
from user import User
from mysqlconnection import connectToMySQL
from flask_bcrypt import  Bcrypt;
import re
app = Flask(__name__)
app.secret_key = "bananas are the best fruit"
