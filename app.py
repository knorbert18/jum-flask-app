import os
import random
import secrets
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from flask_login import confirm_login
import qrcode
import requests
from dotenv import load_dotenv
from flask import (
    Flask, request, jsonify, render_template, redirect, url_for, session, flash, current_app, send_file
)
from flask_cors import CORS
from flask_login import (
    LoginManager, login_user, logout_user, current_user, login_required, UserMixin
)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, User, Product, Order, UserSettings
from admin import init_admin

load_dotenv()

app = Flask(__name__)

# Configurations
app.secret_key = os.getenv('SECRET_KEY', '6dca9fa83f8d8cab0a0aba4731048e1809e9a6bcc5161d40e6193ed479005b2d')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookie only sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JS access to the cookie
app.config['REMEMBER_COOKIE_SECURE'] = True  # If using `remember=True` with login_user()
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(days=30)

# Mail config
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_PERMANENT'] = True  # Make the session last for the lifetime of the user’s browser
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Set session expiration time (optional)

mail = Mail(app)
db.init_app(app)
migrate = Migrate(app, db)

# Paystack API Keys
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY', 'your_public_key_here')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY', 'your_secret_key_here')

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Enable CORS with credentials support
CORS(app, supports_credentials=True)

init_admin(app)

@login_manager.user_loader
def load_user(user_id):
    # Use User.query.get() to retrieve the user
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.LargeBinary, nullable=True)
    shipping_name = db.Column(db.String(255), nullable=True)
    shipping_phone = db.Column(db.String(20), nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_region = db.Column(db.String(100), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.id)


def generate_order_id():
    while True:
        order_id = random.randint(1000000000, 9999999999)
        if not Order.query.filter_by(order_id=order_id).first():
            return order_id


def generate_reference():
    """Generate unique payment reference for Paystack"""
    return str(uuid.uuid4()).replace('-', '')


@app.before_request
def enforce_login():
    print(f"Request endpoint: {request.endpoint}, authenticated: {current_user.is_authenticated}")
    allowed_routes = ['home', 'login', 'signup', 'forgot_password', 'static']
    if request.endpoint and (request.endpoint.startswith('static') or request.endpoint in allowed_routes):
        return
    if not current_user.is_authenticated:
        return redirect(url_for('login'))


@app.route('/')
def home():
    print(f"Is user authenticated: {current_user.is_authenticated}")  # Debug log
    if current_user.is_authenticated:
        print("User is authenticated, redirecting to index")
        return redirect(url_for('index'))
    print("User is not authenticated, rendering login page")
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            print(f"User {current_user.username} is already authenticated, session: {session}")
            return redirect(url_for('index'))
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user, remember=True, fresh=True)
        confirm_login()
        session.permanent = True
        print(f"User {user.username} logged in, session: {session}")
        return jsonify({'success': True, 'message': 'Login successful'}), 200

    return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

@app.route('/check')
def check():
    return jsonify({'authenticated': current_user.is_authenticated})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('cart', None)
    print(f"Logged out, session after logout: {session}")  # Debugging session after logout
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([username, email, password]):
        return jsonify({'message': 'Please fill all fields.'}), 400

    try:
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)

        db.session.add(new_user)
        db.session.commit()

        # Optionally make a specific email admin
        if email == 'khindhonald@example.com':
            new_user.is_admin = True
            db.session.commit()

        return jsonify({'message': 'User  registered successfully!'}), 201
    except Exception as e:
        print('Signup Error:', e)
        return jsonify({'message': 'Email already exists or error occurred.'}), 400


@app.route('/index')
@login_required
def index():
    user = db.session.get(User, current_user.id)
    print(f"Accessing /index: user = {user}, is_admin = {getattr(user, 'is_admin', False)}")
    if not user:
        return redirect(url_for('login'))
    is_admin = getattr(user, 'is_admin', False)
    return render_template('index.html', username=user.username, is_admin=is_admin)


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


@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)


@app.route('/payment', methods=['POST'])
@login_required
def payment():
    name = request.form.get('shipping_name')
    phone = request.form.get('shipping_phone')
    address = request.form.get('shipping_address')
    total_price = request.form.get('total_price', type=float)

    if not all([name, phone, address, total_price]):
        return jsonify({"success": False, "message": "Please fill out all required fields."}), 400

    cart = session.get('cart', [])

    order_id = generate_order_id()

    session['pending_order'] = {
        'order_id': order_id,
        'name': name,
        'phone': phone,
        'address': address,
        'total': total_price,
        'cart': cart
    }

    return render_template('payment.html', order_id=order_id, name=name, total=total_price, email=current_user.email)


@app.route('/pay/<int:amount>')
@login_required
def pay(amount):
    email = current_user.email
    order_id = generate_reference()

    order_info = {
        'order_id': order_id,
        'name': current_user.username,
        'phone': getattr(current_user, 'shipping_phone', ''),
        'address': getattr(current_user, 'shipping_address', ''),
        'total': amount
    }

    session['pending_order'] = order_info

    return render_template(
        "payment.html",
        public_key=PAYSTACK_PUBLIC_KEY,
        email=email,
        amount=amount * 100,
        order_id=order_id,
        reference=order_id
    )


@app.route('/verify_payment')
@login_required
def verify_payment():
    ref = request.args.get('reference')
    if not ref:
        return "Payment reference not provided", 400

    order_info = session.get('pending_order')
    if not order_info:
        return "No pending order found", 400

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    result = response.json()

    if result.get('status') and result.get('data', {}).get('status') == 'success':
        new_order = Order(
            order_id=order_info['order_id'],
            user_id=current_user.id,
            name=order_info['name'],
            phone=order_info['phone'],
            address=order_info['address'],
            payment_method='Paystack',
            total=order_info['total'],
            order_date=datetime.now(),
            shipping_status='Pending',
            delivery_status='Not Delivered',
            delivery_date=datetime.now() + timedelta(days=30)
        )
        db.session.add(new_order)
        db.session.commit()

        session.pop('pending_order', None)
        session['cart'] = []

        return render_template('order.html',
                               order={
                                   'order_id': new_order.order_id,
                                   'order_date': new_order.order_date,
                                   'username': new_order.name,
                                   'shipping_status': new_order.shipping_status,
                                   'delivery_date': new_order.delivery_date,
                                   'delivery_status': new_order.delivery_status,
                                   'total': new_order.total
                               })

    return "Payment verification failed", 400


@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    data = request.get_json()
    shipping = data.get("shipping")
    cart = data.get("cart")
    payment_method = data.get("payment_method")
    order_id = data.get("order_id") or generate_order_id()

    try:
        total = sum(item['price'] * item.get('quantity', 1) for item in cart or [])
        order_date = datetime.now()
        delivery_date = (order_date + timedelta(days=5)) if shipping and shipping.get("country", "").lower() == "ghana" else (order_date + timedelta(days=10))

        order = Order(
            order_id=order_id,
            user_id=current_user.id,
            name=shipping.get("name"),
            phone=shipping.get("phone"),
            address=shipping.get("address"),
            payment_method=payment_method,
            total=total,
            order_date=order_date,
            shipping_status='Pending',
            delivery_status='Not Delivered',
            delivery_date=delivery_date
        )
        db.session.add(order)
        db.session.commit()

        # Clear cart
        session['cart'] = []

        return jsonify({"message": "Order placed successfully!", "order_id": order_id})

    except Exception as e:
        print("Order placement error:", e)
        return jsonify({"message": "Failed to place order."}), 500


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.session.get(User, current_user.id)

    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        password = request.form.get('password')
        if password:
            user.password = generate_password_hash(password)
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(20)
            # Store token in DB or cache with expiration, omitted here for brevity

            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message("Password Reset Request",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f"To reset your password, visit the following link:\n{reset_url}\nIf you did not request this, please ignore."
            mail.send(msg)
            flash('Password reset email sent. Please check your inbox.', 'info')
        else:
            flash('Email not found.', 'warning')
        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Token verification omitted for brevity
    if request.method == 'POST':
        password = request.form.get('password')
        # Find user by token, verify token, omitted here
        # For demo, assume user is current_user or found by token
        user = current_user  # Replace with actual lookup

        if password:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Password reset successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


@app.route('/momo_qr')
def momo_qr():
    qr = qrcode.make("tel:0539896049")
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


@app.route('/orders')
@login_required
def orders():
    orders = Order.query.join(User).add_columns(
        Order.order_id, Order.order_date, User.username
    ).all()
    return render_template('orders.html', orders=orders)


@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.join(User).add_columns(
        Order.order_id, Order.order_date, Order.shipping_status,
        Order.delivery_status, Order.delivery_date, User.username
    ).filter(Order.order_id == order_id).first()

    if not order:
        return 'Order not found', 404

    order_data = {
        'order_id': order.order_id,
        'order_date': order.order_date,
        'shipping_status': order.shipping_status,
        'delivery_status': order.delivery_status,
        'delivery_date': order.delivery_date,
        'username': order.username
    }
    return render_template('order.html', order=order_data)


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

    new_order = Order(
        order_id=generate_order_id(),
        user_id=user_id,
        order_date=datetime.now(),
        shipping_status='Processing',
        delivery_status='Pending',
        delivery_date=datetime.now() + timedelta(days=5)
    )
    db.session.add(new_order)
    db.session.commit()

    return redirect(url_for('order_details', order_id=new_order.order_id))


@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order canceled'}), 200
    return jsonify({'message': 'Order not found'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

