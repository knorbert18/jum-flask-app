from flask import redirect, url_for, request, render_template
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from markupsafe import Markup, escape
from werkzeug.security import generate_password_hash
from wtforms.fields import SelectField
from flask_admin.contrib.sqla.filters import FilterEqual, FilterLike, FilterGreater, FilterSmaller

from models import db, User, Product, Order


# ─────── Admin Access Restriction ─────── #
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


# ─────── User Admin ─────── #
class UserAdmin(SecureModelView):
    column_list = ('id', 'username', 'email', 'is_admin', 'shipping_address')
    form_excluded_columns = ('orders', 'password')
    column_searchable_list = ('username', 'email')
    column_filters = ('is_admin', 'shipping_city', 'shipping_country')


# ─────── Product Admin ─────── #
class ProductAdmin(SecureModelView):
    column_list = ('id', 'name', 'price', 'stock', 'image_preview')
    form_columns = ('name', 'description', 'price', 'stock', 'image')

    def _image_preview(view, context, model, name):
        if model.image:
            return Markup(f'<img src="{escape(model.image)}" style="height: 60px;">')
        return 'No Image'

    column_formatters = {
        'image_preview': _image_preview
    }


# ─────── Order Admin ─────── #
class OrderAdmin(SecureModelView):
    column_list = (
        'id', 'order_id', 'user_id', 'total', 'payment_method',
        'shipping_status', 'delivery_status', 'order_date', 'delivery_date', 'status_badge'
    )
    column_filters = (
        FilterEqual(Order.shipping_status, 'Shipping Status'),
        FilterEqual(Order.delivery_status, 'Delivery Status'),
        FilterLike(Order.payment_method, 'Payment Method'),
        FilterGreater(Order.total, 'Total >'),
        FilterSmaller(Order.total, 'Total <'),
    )
    column_searchable_list = ('order_id', 'name', 'phone')

    form_overrides = {
        'shipping_status': SelectField,
        'delivery_status': SelectField
    }
    form_args = {
        'shipping_status': {
            'choices': [('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')]
        },
        'delivery_status': {
            'choices': [('Pending', 'Pending'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered')]
        }
    }

    def _status_badge(view, context, model, name):
        color_map = {
            'Pending': 'warning',
            'Out for Delivery': 'info',
            'Delivered': 'success'
        }
        status = model.delivery_status or 'Pending'
        color = color_map.get(status, 'secondary')
        return Markup(f'<span class="badge bg-{color}">{status}</span>')

    column_formatters = {
        'status_badge': _status_badge
    }


# ─────── Custom Dashboard View ─────── #
class DashboardView(BaseView):
    @expose('/')
    def index(self):
        total_orders = Order.query.count()
        total_users = User.query.count()
        total_products = Product.query.count()
        revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0.0

        return self.render('admin/dashboard.html',
                           total_orders=total_orders,
                           total_users=total_users,
                           total_products=total_products,
                           revenue=revenue)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


# ─────── Initialize Admin Panel ─────── #
def init_admin(app):
    admin = Admin(app, name='Ransbet Admin', template_mode='bootstrap4')
    admin.add_view(DashboardView(name='Dashboard', endpoint='dashboard'))
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ProductAdmin(Product, db.session))
    admin.add_view(OrderAdmin(Order, db.session))

    # Don't create default admin here — move this to create_tables.py
