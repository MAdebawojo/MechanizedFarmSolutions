import os
import secrets
import signal
import sys
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
            flash('Login successful.', 'success')
            return redirect(url_for('shop'))  # Replace with your logged-in template
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
                # flash('A verification link has been sent to your email. Please check your inbox.', 'success')
                # return redirect(url_for('email_verification_page'))
                return render_template('emailVerificationPage.html')

            except Exception as e:
                flash(f"Error: {e}", 'danger')
        return render_template("userRegistrationPage.html")
    return render_template("userRegistrationPage.html")


@app.route('/verify-email', methods=['POST'])
def email_verification_page():
    return render_template('emailVerificationPage.html')

@app.route('/resend_verification', methods=['POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.json.get('email')  # Assuming you send the email in the request body
        if email:
            user = users.find_one({'email': email})
            if user:
                # Generate a new verification token
                new_verification_token = serializer.dumps(email, salt='email-verification')

                # Update the user's document in the MongoDB database with the new token
                users.update_one({'_id': user['_id']}, {'$set': {'verification_token': new_verification_token}})

                # Send the new verification email
                try:
                    msg = Message('Confirm Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
                    link = url_for('verify_email', token=new_verification_token, _external=True)
                    msg.body = f'Click {link} to activate your account'
                    mail.send(msg)
                    flash('Verification email resent successfully.', 'success')
                    # return jsonify({'message': 'Verification email resent successfully'})
                except Exception as e:
                    flash(f"Error sending email: {str(e)}", 'danger')
                    # return jsonify({'error': f"Error sending email: {str(e)}"}), 500
            else:
                flash('User not found', 'danger')
                # return jsonify({'error': 'User not found'}), 404
        else:
          flash('Email not provided in the request', 'danger')
            # return jsonify({'error': 'Email not provided in the request'}), 400


# --------------------------Authentication End-------------------------------#

# --------------------------Product Data-------------------------------------#
products = [
    {
        "id": 1,
        "name": "Combine Harvester",
        "price": 205000.00,
        "image": "../../static/machineRentals/img/shopImages/product-1.jpg",
        "rating": 5,
        "reviews": 99,
        "description": "The ultimate grain harvesting solution, our Combine Harvester efficiently gathers and threshes crops in a single pass."
    },
    {
        "id": 2,
        "name": "Harrow",
        "price": 123000.00,
        "image": "../../static/machineRentals/img/shopImages/product-2.jpg",
        "rating": 4.5,
        "reviews": 99,
        "description": "A harrow is an implement for breaking up and smoothing out the surface of the soil. In this way it is distinct in its effect from the plough, which is used for deeper tillage."
    },
    {
        "id": 3,
        "name": "Rake",
        "price": 99000.00,
        "image": "../../static/machineRentals/img/shopImages/product-3.jpg",
        "rating": 4,
        "reviews": 99,
        "description": "A rake is a broom for outside use; a horticultural implement consisting of a toothed bar fixed transversely to a handle, and used to collect leaves, hay, grass, etc., and in gardening, for loosening the soil, light weeding and levelling, removing dead grass from lawns, and generally for purposes performed in agriculture by the harrow."
    },
    {
        "id": 4,
        "name": "Roller",
        "price": 321000.00,
        "image": "../../static/machineRentals/img/shopImages/product-4.jpg",
        "rating": 3.5,
        "reviews": 99,
        "description": "A lawn roller is a huge tool that is used for flattening the ground. It is a heavy cylinder that is attached to a handle and is rolled over the ground to flatten it."
    },
    {
        "id": 5,
        "name": "Harvester",
        "price": 123000.00,
        "image": "../../static/machineRentals/img/shopImages/product-5.jpg",
        "rating": 3,
        "reviews": 99,
        "description": "A harvester is a machine that reaps (cuts and often also gathers) grain crops at harvest when they are ripe."
    },
    {
        "id": 6,
        "name": "Sprayer",
        "price": 98000.00,
        "image": "../../static/machineRentals/img/shopImages/product-6.jpg",
        "rating": 4.5,
        "reviews": 99,
        "description": "A sprayer is a device used to spray a liquid, where sprayers are commonly used for projection of water, weed killers, crop performance materials, pest maintenance chemicals, as well as manufacturing and production line ingredients."
    },
    {
        "id": 7,
        "name": "Tractor",
        "price": 456000.00,
        "image": "../../static/machineRentals/img/shopImages/product-7.jpg",
        "rating": 4,
        "reviews": 99,
        "description": "A tractor is an engineering vehicle specifically designed to deliver a high tractive effort (or torque) at slow speeds, for the purposes of hauling a trailer or machinery such as that used in agriculture, mining or construction."
    },
    {
        "id": 8,
        "name": "Roller 2",
        "price": 321000.00,
        "image": "../../static/machineRentals/img/shopImages/product-8.jpg",
        "rating": 3.5,
        "reviews": 99,
        "description": "A lawn roller is a huge tool that is used for flattening the ground. It is a heavy cylinder that is attached to a handle and is rolled over the ground to flatten it."
    }
]
# --------------------------End Product Data---------------------------------#

#--------------------------- Machine Rentals---------------------------------#
@app.route('/machine-rentals/shop')
def shop():
    return render_template("./machineRentals/shop.html", products=products)

# Get product by id
@app.route('/machine-rentals/product/<int:id>')
def product(id):
    product = [product for product in products if product['id'] == id]
    return render_template("./machineRentals/detail.html", products=products, product=product[0])

@app.route('/machine-rentals/cart')
def cart():
    return render_template("./machineRentals/cart.html", products=products)

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

@app.route('/blogs')
def blogs():
    return render_template("./blogs/blogs.html")

@app.route('/blogs/future')
def blogs_future():
    return render_template("./blogs/future.html")

@app.route('/blogs/grants')
def blogs_grants():
    return render_template("./blogs/grants.html")

@app.route('/blogs/maintenance')
def blogs_maintenance():
    return render_template("./blogs/maintenance.html")

@app.route('/blogs/health')
def blogs_health():
    return render_template("./blogs/health.html")

@app.route('/blogs/mechanized-tools')
def blogs_mechanized_tools():
    return render_template("./blogs/mechanized_tools.html")

@app.route('/carbon-emission-calculator')
def carbon_emission():
    return render_template("carbonEmissionsCalc.html")
#---------------------------End Other Pages-------------------------------------#

# if __name__ == "__main__":
#     app.run(debug=True)


def handle_exit(signum, frame):
    print("Received signal to exit. Shutting down gracefully.")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)


if __name__ == "__main__":
    try:
        app.run(debug=False)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
