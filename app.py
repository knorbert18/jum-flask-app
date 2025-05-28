import os
import random
import secrets
import uuid
from datetime import datetime, timedelta
from io import BytesIO

import qrcode
import requests
from dotenv import load_dotenv
from flask import (
    Flask, request, jsonify, render_template, redirect,
    url_for, session, flash, current_app, send_file
)
from flask_cors import CORS
from flask_login import (
    LoginManager, login_user, logout_user, current_user,
    login_required, UserMixin, confirm_login
)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from models import db, User, VerificationCode, Product, Order, OrderItem, CartItem, UserSettings
from admin import init_admin


load_dotenv()

app = Flask(__name__)

# Configurations
app.secret_key = os.getenv('SECRET_KEY', '6dca9fa83f8d8cab0a0aba4731048e1809e9a6bcc5161d40e6193ed479005b2d')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['PAYSTACK_SECRET_KEY'] = os.getenv('PAYSTACK_SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Updated: Allows cross-origin cookie sharing
app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookie only sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JS access to the cookie
app.config['REMEMBER_COOKIE_SECURE'] = True  # If using `remember=True` with login_user()
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(days=30)

# Mail config
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')  # smtp.gmail.com
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))  # 587 is correct for TLS
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'  # Should resolve to True
app.config['MAIL_USE_SSL'] = False  # Correct — SSL is only for port 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Gmail address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # App password (no spaces)
app.config['MAIL_DEBUG'] = True  # Helpful for seeing what goes wrong

mail = Mail(app)
db.init_app(app)
migrate = Migrate(app, db)

# Paystack API Keys
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY', 'pk_test_70ef4a9d7c8591a023c82daff04a1f0c3cc98413')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY', 'sk_test_f1a8fcedf83f8093bd82337279ea9ea2b1d0f652')

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Enable CORS with credentials support
CORS(app, supports_credentials=True, origins=["https://jum-flask-app.onrender.com"])

init_admin(app)

@login_manager.user_loader
def load_user(user_id):
    # Use User.query.get() to retrieve the user
    return User.query.get(int(user_id))

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
    print(f"Logged out, session after logout: {session}")
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

    order_id = generate_order_id()

    # Fetch cart items from DB for current user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    # Prepare cart data for session
    cart_data = []
    for item in cart_items:
        cart_data.append({
            'id': item.product_id,
            'name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.product.price)
        })

    session['pending_order'] = {
        'order_id': order_id,
        'name': name,
        'phone': phone,
        'address': address,
        'total': total_price,
        'cart': cart_data
    }

    return render_template(
        'payment.html',
        order_id=order_id,
        name=name,
        total=total_price,
        email=current_user.email
    )


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


import traceback

@app.route('/verify_payment')
@login_required
def verify_payment():
    reference = request.args.get('reference')
    paystack_secret_key = app.config.get('PAYSTACK_SECRET_KEY')

    if not paystack_secret_key:
        return "Paystack Secret Key is missing in config.", 500

    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
    }

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    result = response.json()

    if result.get('status') and result.get('data', {}).get('status') == 'success':
        order_info = session.get('pending_order')
        if not order_info:
            return "Session expired or invalid order.", 400

        try:
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
            db.session.flush()

            for item in order_info.get('cart', []):
                product = Product.query.get(item['id'])
                if not product:

                    continue

                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item['quantity'],
                    price=item['price']
                )
                db.session.add(order_item)

            db.session.commit()

            # Clear user's cart after order placement
            CartItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()

            session.pop('pending_order', None)
            session['cart'] = []
            cart_count = 0

            return render_template('order.html', order={
                'order_id': new_order.order_id,
                'order_date': new_order.order_date,
                'username': new_order.name,
                'shipping_status': new_order.shipping_status,
                'delivery_date': new_order.delivery_date,
                'delivery_status': new_order.delivery_status,
                'total': new_order.total
            }, cart_count=cart_count)

        except Exception as e:
            print("ORDER SAVE ERROR:", e)
            traceback.print_exc()
            return "Internal server error while saving order.", 500

    return "Payment failed or invalid.", 400

@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    data = request.get_json()
    shipping = data.get("shipping")
    payment_method = data.get("payment_method")
    order_id = data.get("order_id") or generate_order_id()

    try:
        # Fetch user's cart items from DB, not from request JSON
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            return jsonify({"message": "Your cart is empty."}), 400

        # Calculate total from cart items
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        order_date = datetime.now()
        delivery_date = (order_date + timedelta(days=5)) if shipping and shipping.get("country", "").lower() == "ghana" else (order_date + timedelta(days=10))

        # Create Order and flush to get order.id
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
        db.session.flush()

        # Create OrderItems for each cart item
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=float(cart_item.product.price)
            )
            db.session.add(order_item)

        db.session.commit()

        # Clear the cart
        for cart_item in cart_items:
            db.session.delete(cart_item)

        db.session.commit()

        return jsonify({"message": "Order placed successfully!", "order_id": order_id})

    except Exception as e:
        print("Order placement error:", e)
        db.session.rollback()
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

@app.route('/payment/success/<int:order_id>', methods=['GET'])
@login_required
def payment_success(order_id):
    
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
 
    order.payment_method = 'Paystack'
    order.payment_status = 'Paid'
    db.session.commit()
 
    return redirect(url_for('invoice', order_id=order.order_id))

# Serializer for secure token generation
serializer = URLSafeTimedSerializer(app.secret_key)

# Store a 6-digit verification code in the database
def store_verification_code(email, code):
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    VerificationCode.query.filter_by(email=email).delete()  # Remove old codes
    new_code = VerificationCode(email=email, code=code, expires_at=expires_at)
    db.session.add(new_code)
    db.session.commit()

# Verify a code (if you want to use it separately)
def verify_code(email, submitted_code):
    record = VerificationCode.query.filter_by(email=email, code=submitted_code).first()
    if record and not record.is_expired():
        return True
    return False

# Load user from secure token
def get_user_by_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=600)
        return User.query.filter_by(email=email).first()
    except SignatureExpired:
        flash('Reset link expired. Please request a new one.', 'warning')
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash('Invalid reset link.', 'danger')
        return redirect(url_for('forgot_password'))


# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a verification code and token
            verification_code = str(random.randint(100000, 999999))
            token = serializer.dumps(email)
            reset_url = url_for('reset_password', token=token, _external=True)

            # Store code in database
            store_verification_code(email, verification_code)

            # Send email with both the code and link
            msg = Message(
                "Password Reset Request",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = (
                f"Your verification code is: {verification_code}\n\n"
                f"Or click the link to reset your password:\n{reset_url}\n\n"
                "If you did not request this, please ignore this email."
            )
            mail.send(msg)

            flash('A password reset link and code have been sent to your email.', 'info')
        else:
            flash('Email address not found.', 'warning')

        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

# Reset Password Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', token=token))

        user = get_user_by_token(token)

        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Password reset successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired reset link.', 'danger')
            return redirect(url_for('forgot_password'))

    return render_template('reset_password.html', token=token)


@app.route('/momo_qr')
def momo_qr():
    qr = qrcode.make("tel:0539896049")
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


from sqlalchemy.orm import aliased

from flask_login import current_user

@app.route('/orders')
@login_required
def orders():
    orders = db.session.query(
        Order.order_id, Order.order_date, User.username
    ).join(User).filter(Order.user_id == current_user.id).all()
    return render_template('orders.html', orders=orders)

import logging

logging.basicConfig(level=logging.DEBUG)

from flask import after_this_request

@app.route('/invoice/<int:order_id>')
@login_required
def invoice(order_id):
    app.logger.debug(f"Requested invoice for order_id: {order_id}")


    order = Order.query.filter_by(order_id=order_id, user_id=current_user.id).first()
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('orders'))


    order_items = OrderItem.query.filter_by(order_id=order.id).all()


    try:
        net_invoice_value = order.total
        divisor = 1.06 * 1.15
        basic_amount = round(net_invoice_value / divisor, 2)

        covid_levy = round(basic_amount * 0.01, 2)
        getfund = round(basic_amount * 0.025, 2)
        nhil = round(basic_amount * 0.025, 2)

        total_with_levies = round(basic_amount + covid_levy + getfund + nhil, 2)
        vat = round(total_with_levies * 0.15, 2)

    except Exception as e:
        app.logger.error(f"Tax calculation error: {e}")
        basic_amount = covid_levy = getfund = nhil = total_with_levies = vat = 0
        net_invoice_value = order.total



    return render_template(
        'invoice.html',
        order=order,
        order_items=order_items,
        basic_amount=basic_amount,
        covid_levy=covid_levy,
        getfund=getfund,
        nhil=nhil,
        total_with_levies=total_with_levies,
        vat=vat,
        net_invoice_value=net_invoice_value
    )


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

@app.route('/order/<int:order_id>/invoice')
@login_required
def order_invoice(order_id):
    
    order = Order.query.filter_by(order_id=order_id).first_or_404()

    user = order.user

    
    order_items = OrderItem.query.filter_by(order_id=order.id).join(Product).add_columns(
        Product.name, OrderItem.quantity, Product.price).all()

    subtotal = sum(item.quantity * float(item.price) for _, item in enumerate(order_items))
    
    subtotal = 0
    for oi in order_items:
       
        pass


    subtotal = 0
    for order_item in order.items:
        subtotal += order_item.quantity * float(order_item.product.price)

    tax = subtotal * 0.1
    total = subtotal + tax

    return render_template(
        'invoice.html',
        order=order,
        user=user,
        order_items=order.items,
        subtotal=subtotal,
        tax=tax,
        total=total
    )


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

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart_route():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/cart', methods=['GET', 'POST'])
@login_required
def api_cart():
    if request.method == 'GET':
        
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_data = [{
            'product_id': item.product_id,
            'quantity': item.quantity,
            'product': {
                'id': item.product.id,
                'name': item.product.name,
                'price': item.product.price,
                'image': item.product.image,
            }
        } for item in cart_items]
        return jsonify({'cart': cart_data})

    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        product_id = data.get('id')
        if not product_id:
            return jsonify({'error': 'Product ID required'}), 400

        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
            db.session.add(cart_item)

        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/cart/count')
@login_required
def cart_count():
    count = db.session.query(db.func.sum(CartItem.quantity))\
                      .filter_by(user_id=current_user.id)\
                      .scalar() or 0
    return jsonify({'count': count})

@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart_item():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or quantity is None:
        return jsonify({'error': 'Invalid data'}), 400

    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity = quantity
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Item not found'}), 404

@app.route('/api/cart/delete', methods=['POST'])
@login_required
def delete_cart_item():
    data = request.get_json()
    product_id = data.get('product_id')

    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Item not found'}), 404

@app.route('/api/products/seed', methods=['POST'])
def seed_products():
    products = request.json
    
    for p in products:
        existing_product = Product.query.get(p['id'])
        if existing_product:
            continue
        
        new_product = Product(
            id=p['id'],
            name=p['name'],
            price=p['price'],
            image=p.get('image'),
        )
        db.session.add(new_product)
    
    db.session.commit()
    return jsonify({"message": "Products seeded successfully"}), 201

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_list = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image": p.image,
            "category": getattr(p, 'category', '')  # if you store category
        } for p in products
    ]
    return jsonify(products_list)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        shipping_name = request.form.get('shipping_name')
        shipping_phone = request.form.get('shipping_phone')
        shipping_address = request.form.get('shipping_address')
        shipping_city = request.form.get('shipping_city') or 'Accra'
        shipping_region = request.form.get('shipping_region')
        shipping_country = request.form.get('shipping_country') or 'Ghana'

        if not all([shipping_name, shipping_phone, shipping_address, shipping_region]):
            flash('Please fill in all the fields!', 'error')
            return redirect(url_for('checkout'))

        user = User.query.get(current_user.id)
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('checkout'))

        # Update user's shipping info
        user.shipping_name = shipping_name
        user.shipping_phone = shipping_phone
        user.shipping_address = shipping_address
        user.shipping_city = shipping_city
        user.shipping_region = shipping_region
        user.shipping_country = shipping_country

        # Create the order
        new_order = Order(
            user_id=user.id,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_region=shipping_region,
            shipping_country=shipping_country,
            created_at=datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.flush() 

        # Move items from cart to order
        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        if not cart_items:
            flash("Your cart is empty!", "error")
            return redirect(url_for('cart'))

        for cart_item in cart_items:
            db.session.add(OrderItem(
                order_id=new_order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity
            ))

        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('verify_payment')) 

    return render_template('checkout.html')

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(order_id=order_id, user_id=current_user.id).first()
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order canceled'}), 200
    return jsonify({'message': 'Order not found'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

