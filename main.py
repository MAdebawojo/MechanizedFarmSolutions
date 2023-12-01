import os
import secrets
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_URI = os.getenv('DATABASE_URI')
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'adebawojomosope@gmail.com'
app.config['MAIL_PASSWORD'] = 'ogtl zeui lclf whgo'
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = True

# Initialize the MongoDB client
try:
    client = MongoClient(DATABASE_URI)
    # Get the database
    db = client.get_database(DATABASE_NAME)
    # Get the 'user_accounts' collection
    users = db.UserRegistrationRecords
except Exception as e:
    print(f"MongoDB connection error: {e}")
    raise e

bcrypt = Bcrypt(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# --------------------------Authentication- Begin------------------------------#
@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    """ Email verification route"""
    try:
        email = serializer.loads(token, salt='email-verification', max_age=1440)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    except BadSignature:
        return '<h1>The token is not valid!</h1>'
    except Exception as e:
        return f'<h1>An error: {e} occured'
    user = users.find_one({'verification_token': token})
    if user:
        # User found with a matching verification token
        if not user.get('email_verified', False):
            # Mark the email as verified and remove the verification token
            users.update_one({'_id': user['_id']}, {'$set': {'email_verified': True, 'verification_token': ''}})
            flash('Your email has been verified. You can now log in.', 'success')
        else:
            flash('Email already verified. You can log in.', 'info')
            return redirect(url_for('userLoginPage'))
    else:
        flash('Invalid or expired verification token.', 'danger')
    return redirect(url_for('login'))

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form.get('password')
        user = users.find_one({'email': email})
        if user and bcrypt.check_password_hash(user.get('password', ''), password):
            return render_template("try.html")  # Replace with your logged-in template
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template("userLoginPage.html")

@app.route('/register/', methods=['POST', 'GET'])
def register():
    """User Registration route"""
    if request.method == 'POST':
        f_name = request.form['firstName']
        l_name = request.form['lastName']
        phoneNumber = request.form['phoneNumber']
        email = request.form['email']
        password = request.form.get('password')
        existing_user = users.find_one({'email': email})
        if existing_user:
            flash('Registration failed. Email is already in use.', category='danger')
        elif not password:
            flash('Password cannot be empty', category='danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            verification_token = serializer.dumps(email, salt='email-verification')

            # Save the token and user's email status in the database
            new_user = {
                'firstName': f_name,
                'lastName': l_name,
                'phoneNumber': phoneNumber,
                'email': email,
                'password': hashed_password,
                'email_verified': False,
                'verification_token': verification_token,
            }

            try:
                users.insert_one(new_user)
                msg = Message('Confirm Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
                link = url_for('verify_email', token=verification_token, external=True)
                msg.body = f'Click 127.0.0.1:5000{link} to activate your account'
                mail.send(msg)
                flash('A verification link has been sent to your email. Please check your inbox.', 'success')
                return redirect(url_for('userLoginPage'))
            except Exception as e:
                flash(f"Error: {e}", 'danger')
        return render_template("userRegistrationPage.html")
    return render_template("userRegistrationPage.html")

# --------------------------Authentication End-------------------------------#

#--------------------------- Machine Rentals---------------------------------#
@app.route('/machine-rentals/shop')
def shop():
    return render_template("./machineRentals/shop.html")

@app.route('/machine-rentals/cart')
def cart():
    return render_template("./machineRentals/cart.html")

@app.route('/machine-rentals/detail')
def detail():
    return render_template("./machineRentals/detail.html")

@app.route('/machine-rentals/checkout')
def checkout():
    return render_template("./machineRentals/checkout.html")
#---------------------------End Machine Rentals---------------------------------#

#---------------------------Other Pages----------------------------------------#

@app.route('/')
@app.route('/home')
def home():
    return render_template("homePage.html")

@app.route('/contact-us')
def contact_us():
    return render_template("contactUsPage.html")

@app.route('/testimonials')
def testimonials():
    return render_template("testimonials.html")

@app.route('/our-team')
def our_team():
    return render_template("ourTeam.html")

@app.route('/about-us')
def about_us():
    return render_template("about-us.html")
#---------------------------End Other Pages-------------------------------------#

if __name__ == "__main__":
    app.run(debug=True)








































# import json
# from flask import Flask, session, flash, jsonify, url_for, render_template, request, redirect
# from flask_bcrypt import Bcrypt
# from pymongo import MongoClient, errors
# # from bson import ObjectId
# import os
# from dotenv import load_dotenv
#
# load_dotenv(dotenv_path='.env')
#
# DATABASE_NAME = os.getenv('DATABASE_NAME')
# DATABASE_URI = os.getenv('DATABASE_URI')
# SECRET_KEY = os.getenv('SECRET_KEY')
#
#
# app = Flask(__name__)
# app.secret_key = SECRET_KEY
#
# # Initialize the MongoDB client
# try:
#     client = MongoClient(DATABASE_URI)
#     # Get the database
#     db = client.get_database(DATABASE_NAME)
#     # Get the 'user_accounts' collection
#     users = db.UserRegistrationRecords
#     # # Get the 'user_books' collection
#     # user_books = db.user_accounts
#     # # Access the MongoDB collections (books)
#     # books_collection = db.books
# except Exception as e:
#     print(f"MongoDB connection error: {e}")
#     raise e
#
# bcrypt = Bcrypt(app)
#
#
# @app.route('/register/', methods=['POST', 'GET'])
# def register():
#     if request.method == 'POST':
#         f_name = request.form['firstName']
#         l_name = request.form['lastName']
#         phoneNumber = request.form['phoneNumber']
#         email = request.form['email']
#         password = request.form.get('password')
#         print(f_name + ' ' + l_name + ' ' + phoneNumber + ' ' + email + ' ' + password)
#         existing_user = users.find_one({'email': email})
#         if existing_user:
#             flash('Registration failed. Email is already in use.', category='danger')
#         elif not password:
#             flash('Password cannot be empty', category='danger')
#         else:
#             hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#             # hashed_password = password
#             print(hashed_password)
#             new_user = {
#                 'firstName': f_name,
#                 'lastName': l_name,
#                 'phoneNumber': phoneNumber,
#                 'email': 'email',
#                 'password': hashed_password
#             }
#
#             print(new_user)
#             try:
#                 users.insert_one(new_user)
#                 flash('Your account has been created! You are now able to log in.', category='success')
#                 return redirect(url_for('userLoginPage'))
#             except Exception as e:
#                 print(f"MongoDB insertion error: {e}")
#                 flash(f"Connection error: {e}")
#     return render_template("userRegistrationPage.html")
#
#
# if __name__ == "__main__":
#     app.run(debug=True)

































# @app.route('/')
# def home():
#     return render_template("index.html")
#
# @app.route('/about')
# def about():
#     return render_template("about.html")

# @app.route('/login/', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form.get('password')
#
#         try:
#             user = users.find_one({'email': email})
#             print(user['username'])
#         except Exception as e:
#             print(f"MongoDB query error: {e}")
#             flash(f"Connection error: {e}")
#         else:
#             if user and bcrypt.check_password_hash(user.get('password', ''), password):
#                 session['email'] = email
#                 session['username'] = user['username']
#                 print(f"Session: {session['username']}")
#                 return redirect(url_for("library", email=email))
#             else:
#                 flash('Login unsuccessful. Please check email and password', 'danger')
#     return render_template("login.html")