from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))

    # Shipping Info
    shipping_name = db.Column(db.String(255))
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_region = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100))

    payment_method = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    orders = db.relationship('Order', back_populates='user', lazy=True)
    settings = db.relationship('UserSettings', backref='user', uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"

# User Settings Model
class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    language = db.Column(db.String(10), default='en')
    dark_mode = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<UserSettings UserID={self.user_id}>"

# Product Model
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))

    # Relationship to OrderItem
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"

# Order Model
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.BigInteger, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))

    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='Pending')
    total = db.Column(db.Float)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    shipping_status = db.Column(db.String(50), default='Pending')
    delivery_status = db.Column(db.String(50), default='Not Shipped')
    delivery_date = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    items = db.relationship(
        'OrderItem',
        back_populates='order',
        lazy=True,
        cascade='all, delete-orphan'
    )

    @property
    def computed_total(self):
        return sum(item.total_price for item in self.items)

    def subtotal(self):
        return sum(item.price for item in self.items)

    @property
    def tax(self):
        return self.subtotal() * 0.10

    @property
    def total_with_tax(self):
        return self.subtotal() + self.tax

    def __repr__(self):
        return f"<Order {self.order_id}>"

# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(100))  # Snapshot of product name at order time
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')

    @property
    def total_price(self):
        return float(self.quantity) * float(self.price)

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity}>"

# CartItem Model
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product')

    @property
    def total_price(self):
        """Calculates the total price for this cart item."""
        return float(self.quantity) * float(self.product.price)

    def __repr__(self):
        return f"<CartItem user_id={self.user_id}, product_id={self.product_id}, qty={self.quantity}>"
