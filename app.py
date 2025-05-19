from flask import (Flask, request, jsonify, render_template, redirect, url_for, session, flash, current_app, send_file)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import random
import secrets
from io import BytesIO
import qrcode
import psycopg2
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product, Order
from admin import init_admin
from flask import Flask, render_template, request, redirect
import uuid, requests

from flask_login import UserMixin  # Ensure this import

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Keeps table definitions in sync

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(128), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    
    # Add the 'is_active' column to the User model
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.id)  # Flask-Login uses this to get the user ID

    
def generate_order_id():
    while True:
        order_id = random.randint(1000000000, 9999999999)
        if not Order.query.filter_by(order_id=order_id).first():
            return order_id

app = Flask(__name__)

# Paystack API Keys
PAYSTACK_PUBLIC_KEY = "pk_live_b4fa73434e9fd1fb08b38b8c19b3d9056660408b"
PAYSTACK_SECRET_KEY = "sk_live_78d67f6e32fed3246caab25680b520c646bb630c"

def generate_reference():
    """Generate a unique reference ID for each transaction"""
    return str(uuid.uuid4()).replace('-', '')

@app.route("/pay/<int:amount>")
def pay(amount):
    email = current_user.email  # Ideally, fetch from logged-in user
    order_id = generate_reference()  # Or fetch an actual order_id
    # Example order data (this would normally come from your cart or order system)
    order_info = {
        'order_id': order_id,
        'name': current_user.name,
        'phone': current_user.phone,
        'address': current_user.address,
        'total': amount
    }

    # Store order info in session
    session['pending_order'] = order_info

    return render_template("payment.html", 
                           public_key=PAYSTACK_PUBLIC_KEY,
                           email=email,
                           amount=amount * 100,
                           order_id=order_id,  # Send this to the payment page
                           reference=order_id)  # Same here for reference


@app.route('/verify_payment')
def verify_payment():
    ref = request.args.get('reference')
    if not ref:
        return "Payment reference not provided", 400

    # Get the pending order from the session
    order_info = session.get('pending_order')
    if not order_info:
        return "No pending order found", 400

    # Now verify the payment with Paystack API
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    result = response.json()

    if result['status'] and result['data']['status'] == 'success':
        # After payment success, store the order into your database
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO orders (
                order_id, user_id, name, phone, address,
                payment_method, total, order_date,
                shipping_status, delivery_status, delivery_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            order_info['order_id'],
            current_user.id,
            order_info['name'],
            order_info['phone'],
            order_info['address'],
            'Paystack',
            order_info['total'],
            datetime.now(),
            'Pending',
            'Not Delivered',
            datetime.now() + timedelta(days=30)
        ))
        conn.commit()
        cur.close()

        # Clear session data (cart and pending order)
        session.pop('pending_order', None)
        session['cart'] = []  # Clear cart

        # Send the order details to the 'order.html' template for confirmation
        return render_template('order.html', 
                               order={
                                   'order_id': order_info['order_id'],
                                   'order_date': datetime.now(),
                                   'username': order_info['name'],
                                   'shipping_status': 'Pending',
                                   'delivery_date': datetime.now() + timedelta(days=30),
                                   'delivery_status': 'Not Delivered',
                                   'total': order_info['total']
                               })
    
    return "Payment verification failed", 400

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:cAndy12$@dpg-ck0mhij6fquc73862au0-a.oregon-postgres.render.com:5432/JUMIA?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

init_admin(app)

with app.app_context():
    db.create_all()
    
CORS(app, supports_credentials=True)
app.secret_key = '2e1f58e873055c64455686eac64f65d5046b2f31c33633a4e45970a6ea91a63a'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'  # or your login route name

@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(User, int(user_id))

conn = psycopg2.connect(
    dbname="JUMIA",
    user="postgres",
    password="cAndy12$",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def initialize_tables():
    cur.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            password VARCHAR(255),
            avatar bytea,
            shipping_name VARCHAR(255),
            shipping_phone VARCHAR(20),
            shipping_address TEXT,
            shipping_city VARCHAR(100),
            shipping_region VARCHAR(100),
            shipping_country VARCHAR(100),
            payment_method VARCHAR(50),
            is_admin BOOLEAN DEFAULT FALSE,  -- ✅ Add this
            reset_token VARCHAR(100),        -- ✅ Add this
            reset_token_expiration TIMESTAMP -- ✅ And this
);
    ''')

    cur.execute(''' 
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_id BIGINT UNIQUE,
            user_id INTEGER REFERENCES users(id),
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            total NUMERIC(10, 2),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shipping_status VARCHAR(50) DEFAULT 'Pending',  -- Add this column
            delivery_status VARCHAR(50) DEFAULT 'Not Delivered',
            delivery_date TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) UNIQUE,
            language VARCHAR(50) DEFAULT 'English',
            timezone VARCHAR(50) DEFAULT 'UTC',
            theme VARCHAR(10) DEFAULT 'light',
            email_notifications BOOLEAN DEFAULT TRUE,
            sms_notifications BOOLEAN DEFAULT TRUE,
            two_factor_enabled BOOLEAN DEFAULT FALSE
        )
    ''')

    conn.commit()

initialize_tables()

@app.before_request
def enforce_login():
    # Skip login check for these routes
    allowed_routes = ['home', 'login', 'signup', 'forgot_password', 'static']
    if request.endpoint and (request.endpoint.startswith('static') or request.endpoint in allowed_routes):
        return

    # Let Flask-Login handle authentication
    if not current_user.is_authenticated:
        return redirect(url_for('login'))


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    orders_count = Order.query.count()
    products_count = Product.query.count()
    users_count = User.query.count()
    return render_template(
        'admin.html',
        orders=orders_count,
        products=products_count,
        users=users_count
    )

from flask import jsonify

from flask import render_template, request, jsonify, session
from flask_login import login_required, current_user
import random

@app.route('/payment', methods=['POST'])
@login_required
def payment():
    name = request.form.get('shipping_name')
    phone = request.form.get('shipping_phone')
    address = request.form.get('shipping_address')
    total_price = request.form.get('total_price', type=float)  # Read total price from form

    if not all([name, phone, address, total_price]):
        return jsonify({"success": False, "message": "Please fill out all required fields."}), 400

    cart = session.get('cart', [])  # Optional: you may want to set session cart from localStorage in the future

    order_id = random.randint(1000000000, 9999999999)  # Generate random order_id

    # Save necessary info in session for use after payment
    session['pending_order'] = {
        'order_id': order_id,
        'name': name,
        'phone': phone,
        'address': address,
        'total': total_price,
        'cart': cart
    }

    # Pass 'email' along with other info for rendering in the template
    return render_template('payment.html', order_id=order_id, name=name, total=total_price, email=current_user.email)

@app.route('/index')
@login_required
def index():
    user = db.session.get(User, current_user.id)
    if not user:
        return redirect(url_for('login'))
    is_admin = user.is_admin if hasattr(user, 'is_admin') else False
    return render_template('index.html', username=user.username, is_admin=is_admin)

@app.route("/about")
def about():
    from datetime import datetime
    return render_template("about.html", current_year=datetime.now().year)

@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    data = request.get_json()
    shipping = data.get("shipping")
    cart = data.get("cart")
    payment_method = data.get("payment_method")
    order_id = data.get("order_id")  # Expect existing order_id from frontend

    if not order_id:
        # Fallback: generate new order_id only if none is provided (optional)
        order_id = generate_order_id()

        try:
            total = sum(item['price'] * item.get('quantity', 1) for item in cart or [])
            order_date = datetime.now()
            delivery_date = calculate_delivery_date(
                shipping.get("city", "Accra"),
                shipping.get("country", "Ghana"),
                order_date
            ) if shipping else order_date + timedelta(days=30)

            cur.execute("""
                INSERT INTO orders (
                    order_id, user_id, name, phone, address, payment_method,
                    total, order_date, shipping_status, delivery_status, delivery_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                current_user.id,
                shipping.get("name", "Guest"),
                shipping.get("phone", "N/A"),
                shipping.get("address", "Unknown"),
                payment_method or "Unknown",
                total,
                order_date,
                "Confirmed",
                "Not Delivered",
                delivery_date
            ))
            conn.commit()

        except Exception as e:
            print("Payment error:", e)
            conn.rollback()

    else:
        # Optionally: update the payment method or status for existing order_id
        try:
            cur.execute("""
                UPDATE orders SET payment_method = %s WHERE order_id = %s AND user_id = %s
            """, (payment_method, order_id, current_user.id))
            conn.commit()
        except Exception as e:
            print("Update payment method error:", e)
            conn.rollback()

    return jsonify(success=True, order_id=order_id)

from flask import request, jsonify

payment_status = {}

@app.route('/simulate_payment', methods=['POST'])
@login_required
def simulate_payment():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        if not order_id:
            return jsonify({"success": False, "error": "Missing order_id"}), 400
        
        # Simulate payment confirmation logic (e.g., update DB)
        payment_status[order_id] = "confirmed"
        
        # Optionally update your order status in the database here
        
        return jsonify({"success": True, "order_id": order_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # Get user from session (you appear to be using raw SQL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', (current_user.email,))
    user = cur.fetchone()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('home'))

    user_id = user[0]
    username = user[1]

    # Get or create settings
    cur.execute('SELECT * FROM user_settings WHERE user_id = %s', (user_id,))
    settings = cur.fetchone()
    if not settings:
        cur.execute('INSERT INTO user_settings (user_id) VALUES (%s)', (user_id,))
        conn.commit()
        cur.execute('SELECT * FROM user_settings WHERE user_id = %s', (user_id,))
        settings = cur.fetchone()

    # Handle POST updates
    if request.method == 'POST':
        # Update avatar if uploaded
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar and avatar.filename != '':
                avatar_filename = secure_filename(avatar.filename)
                avatar_path = os.path.join('static', 'avatars', avatar_filename)
                avatar.save(avatar_path)
                cur.execute('UPDATE users SET avatar = %s WHERE id = %s', (avatar_filename, user_id))
                conn.commit()
                flash('Avatar updated successfully.', 'success')

        # Update phone
        phone = request.form.get('phone')
        cur.execute('UPDATE users SET shipping_phone = %s WHERE id = %s', (phone, user_id))

        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if current_password and new_password and new_password == confirm_password:
            if check_password_hash(user[3], current_password):
                hashed_pw = generate_password_hash(new_password)
                cur.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_pw, user_id))
            else:
                flash('Incorrect current password.', 'error')
                return redirect(url_for('account'))

        # Update settings
        language = request.form.get('language')
        timezone = request.form.get('timezone')
        theme = request.form.get('theme')
        email_notifications = 'email_notifications' in request.form
        sms_notifications = 'sms_notifications' in request.form
        two_factor_enabled = 'two_factor_enabled' in request.form

        cur.execute('''
            UPDATE user_settings
            SET language = %s, timezone = %s, theme = %s,
                email_notifications = %s, sms_notifications = %s, two_factor_enabled = %s
            WHERE user_id = %s
        ''', (language, timezone, theme, email_notifications, sms_notifications, two_factor_enabled, user_id))

        conn.commit()
        flash('Account updated successfully.', 'success')
        return redirect(url_for('account'))

    # Handle avatar display
    avatar_url = url_for('static', filename='avatars/default-avatar.jpg')
    if user[4]:  # assuming user[4] stores avatar filename
        avatar_url = url_for('static', filename=f'avatars/{user[4]}')

    return render_template('account.html', user=user, settings=settings, username=username, avatar_url=avatar_url, is_admin=user[7])

@app.route('/cart')
@login_required
def cart():
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Please fill all fields.'}), 400

    hashed_password = generate_password_hash(password)

    try:
        is_admin = True if email == 'khindhonald@example.com' else False
        cur.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', 
                    (username, email, hashed_password))
        conn.commit()

        if is_admin:
            user = User.query.filter_by(email=email).first()
            if user:
                user.is_admin = True
                db.session.commit()

        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        print('Signup Error:', e)
        return jsonify({'message': 'Email already exists or error occurred.'}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if current_user.is_authenticated:
        return jsonify({'success': True, 'message': 'Already logged in'}), 200

    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True, 'message': 'Login successful'}), 200

    return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

from flask_mail import Mail, Message

app.config.update(
    MAIL_SERVER='smtp.example.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your-email@example.com',
    MAIL_PASSWORD='your-email-password'
)
mail = Mail(app)

reset_tokens = {}

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def update_user_password(email, hashed_password):
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = hashed_password
        db.session.commit()
        return True
    return False

def get_user_by_email(email):
    # Example using SQLAlchemy, case-insensitive email search
    return User.query.filter(User.email.ilike(email.strip())).first()

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Please enter your email address.', 'warning')
            return redirect(url_for('forgot_password'))

        user = get_user_by_email(email)
        if user:
            # Generate a secure token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)  # valid 1 hour
            db.session.commit()

            reset_link = url_for('reset_password', token=token, _external=True)

            msg = Message(
                'Password Reset Request',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = (
                f"Hello,\n\n"
                f"You requested a password reset. Click the link below to reset your password:\n\n"
                f"{reset_link}\n\n"
                f"If you did not request this, please ignore this email.\n\n"
                f"Thank you."
            )
            try:
                mail.send(msg)
                flash('Password reset link sent to your email.', 'success')
            except Exception as e:
                flash('Failed to send email. Please try again later.', 'danger')
                print(f"Mail sending error: {e}")
        else:
            flash('Email address not found.', 'warning')

        return redirect(url_for('forgot_password'))

    # GET request renders the forgot password form
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.reset_token_expiration or user.reset_token_expiration < datetime.utcnow():
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('reset_password', token=token))

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('reset_password', token=token))

        user.password = generate_password_hash(password)
        user.reset_token = None  # invalidate token
        user.reset_token_expiration = None
        db.session.commit()

        flash('Your password has been updated. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    logout_user()
    session.pop('cart', None)
    return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = current_user.username
        shipping_name = request.form.get('shipping_name')
        shipping_phone = request.form.get('shipping_phone')
        shipping_address = request.form.get('shipping_address')
        shipping_city = request.form.get('shipping_city') or 'Accra'
        shipping_region = request.form.get('shipping_region')
        shipping_country = request.form.get('shipping_country') or 'Ghana'

        if not all([shipping_name, shipping_phone, shipping_address, shipping_region]):
            flash('Please fill in all the fields!', 'error')
            return redirect(url_for('checkout'))

        cur.execute('SELECT id FROM users WHERE username = %s', (username,))
        user_id_result = cur.fetchone()
        if not user_id_result:
            flash('User not found!', 'error')
            return redirect(url_for('checkout'))
        user_id = user_id_result[0]

        # Save shipping info in user profile
        cur.execute('''
            UPDATE users
            SET shipping_name = %s, shipping_phone = %s, shipping_address = %s,
                shipping_city = %s, shipping_region = %s, shipping_country = %s
            WHERE id = %s
        ''', (shipping_name, shipping_phone, shipping_address, shipping_city, shipping_region, shipping_country, user_id))
        conn.commit()

        # Save user_id in session for next step (payment)
        session['user_id'] = user_id

        return redirect(url_for('payment'))

    return render_template('checkout.html')


def calculate_delivery_date(city, country, order_date):
    if city in ['Accra', 'Kumasi'] and country == 'Ghana':
        return order_date + timedelta(days=5)
    elif country == 'Ghana':
        return order_date + timedelta(days=10)
    else:
        return order_date + timedelta(days=30)
    
@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    data = request.get_json()
    print("ORDER RECEIVED:", {
        "shipping": data["shipping"],
        "cart": data["cart"],
        "method": data["method"],
        "timestamp": datetime.datetime.now().isoformat()
    })
    return jsonify({"message": "Order stored successfully!"}), 200

@app.route('/orders')
@login_required
def orders():
    cur.execute(''' 
        SELECT o.order_id, o.order_date, u.username 
        FROM orders o
        JOIN users u ON o.user_id = u.id
    ''')
    orders = cur.fetchall()
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    cur.execute(''' 
        SELECT o.order_id, o.order_date, o.shipping_status, o.delivery_status, o.delivery_date, u.username
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.order_id = %s
    ''', (order_id,))
    order = cur.fetchone()

    if order:
        order_data = {
            'order_id': order[0],
            'order_date': order[1],
            'shipping_status': order[2],
            'delivery_status': order[3],
            'delivery_date': order[4],
            'username': order[5]
        }
        return render_template('order.html', order=order_data)
    else:
        return 'Order not found', 404

@app.route('/momo_qr')
def momo_qr():
    import qrcode
    from io import BytesIO
    from flask import send_file

    momo_number = "tel:0539896049"
    qr = qrcode.make(momo_number)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

@app.route('/order')
@login_required
def order_query_redirect():
    order_id = request.args.get('order_id')
    if order_id and order_id.isdigit():
        return redirect(url_for('order_details', order_id=int(order_id)))
    return 'Invalid or missing order ID', 400

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    order_date = datetime.now()
    shipping_status = 'Processing'
    delivery_status = 'Pending'
    delivery_date = order_date + timedelta(days=5)

    order_id = generate_order_id()

    cur.execute('''
        INSERT INTO orders (order_id, user_id, order_date, shipping_status, delivery_status, delivery_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (order_id, user_id, order_date, shipping_status, delivery_status, delivery_date))

    conn.commit()

    return redirect(url_for('order_details', order_id=order_id))

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    try:
        cur.execute('DELETE FROM orders WHERE order_id = %s', (order_id,))
        conn.commit()
        flash('Order canceled successfully!', 'success')
    except Exception as e:
        flash(f'Error canceling order: {e}', 'error')
    return redirect(url_for('orders'))

if __name__ == '__main__':

    app.run(port=5000, debug=True)
init_admin(app)
