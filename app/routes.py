from app import app, db
from flask import render_template, url_for, redirect, flash, request, session
from app.forms import LoginForm, RegistationForm, AddProductForm, ManageUser, AddUserForm, UpdateUserForm, DeleteUserForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Product
from werkzeug.urls import url_parse
import braintree 
from app.gateway import *

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]


@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect email or password. Please try again!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="Log In", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been successfully created!')
        login_user(user)
    return render_template('login.html', title="Register", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title="Profile")

@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    if current_user.admin == 0:
        redirect(url_for('index'))
        flash('You do not have access to that page. Please contact your administrator.')
    form = AddProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, image=form.image.data, stock=form.stock.data)
        db.session.add(product)
        db.session.commit()
        flash('You successfully added {}'.format(product.name))
        return redirect(url_for('inventory'))
    return render_template('addproduct.html', form=form, title="Add Product")

@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    if current_user.admin == 0:
        redirect(url_for('index'))
        flash('You do not have access to that page. Please contact your administrator.')
    products = Product.query.all()
    return render_template('inventory.html', products=products, title="Inventory")

@app.route('/products', methods=['GET', 'POST'])
def products():
    products = Product.query.all()
    return render_template('products.html', products=products, title="Products")

@app.route('/admin_manage_user', methods=['GET', 'POST'])
@login_required
def admin_manage_user():
    roles = User.query.all()
    role = User.query.filter_by(id=current_user.id).first()
    if current_user.admin == 0:
        redirect(url_for('index'))
        flash('You do not have access to that page. Please contact your administrator.')
    form = ManageUser()
    if form.validate_on_submit() and form.action.data == 'add':
      return redirect(url_for('add_user'))
    if form.validate_on_submit() and form.action.data == 'update':
        return redirect(url_for('update_user'))
    if form.validate_on_submit() and form.action.data == 'delete':
        return redirect(url_for('delete_user'))
    return render_template('admin.html', title="Admin Add User", form=form, roles=roles)
    
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    roles = User.query.all()
    role = User.query.filter_by(id=current_user.id).first()
    if current_user.admin == 0:
        redirect(url_for('index'))
        flash('You do not have access to that page. Please contact your administrator.')
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.first_name.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully created {} {}\'s account!'.format(user.first_name, user.last_name))
        return redirect(url_for('admin_manage_user'))
    return render_template('admin_update_user.html', title="Add User", form=form, roles=roles)

@app.route('/update_user/<id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    roles = User.query.all()
    role = User.query.filter_by(id=current_user.id).first()
    user = User.query.filter_by(id=id).first()
    if current_user.admin == 0:
        redirect(url_for('index'))
        flash('You do not have access to that page. Please contact your administrator.')
    form = UpdateUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.admin = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated {} {}\'s account!'.format(user.first_name, user.last_name))
        return redirect(url_for('admin_manage_user'))
    return render_template('admin_update_user.html', title="Update {} {}\'s Account".format(user.first_name, user.last_name), form=form, roles=roles)

@app.route('/delete_user/<id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    roles = User.query.all()
    role = User.query.filter_by(id=current_user.id).first()
    user = User.query.filter_by(id=id).first()
    name = user.first_name + " " + user.last_name
    if current_user.admin == 0:
        redirect(url_for('index'))
        flash('You do not have access to that page. Please contact your administrator.')
    form = DeleteUserForm()
    if form.validate_on_submit():
        User.query.filter_by(id=id).delete()
        User.query.filter_by(id=id).delete()
        db.session.commit()
        flash('You have successfully deleted {}\'s account!'.format(name))
        return redirect(url_for('admin_manage_user'))
    return render_template('admin_update_user.html', title="Confirm Delete: {}".format(name), form=form, roles=roles)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(id)
    flash("Item added to cart")
    return redirect(url_for('products'))

@app.route('/cart')
def cart():
    if "cart" not in session:
        flash("There is nothing in your cart yet")
        return render_template('cart.html', display_cart={}, total=0)
    items = session["cart"]
    dict_of_items = {}
    total_price = 0
    for item in items:
        product = Product.query.get(item)
        total_price += product.price
        if product.id in dict_of_items:
            dict_of_items[product.id]["qty"] += 1
        else:
            dict_of_items[product.id] = {"qty": 1, "image": product.image, "name": product.name, "price": product.price}
    return render_template('cart.html', title="My Cart", display_cart=dict_of_items, total=total_price)

@app.route('/clear_cart')
def clear_cart():
    del session["cart"]
    return redirect(url_for('cart'))

@app.route('/checkouts/new', methods=['GET', 'PSOT'])
def checkout_new():
    client_token = generate_client_token()
    return render_template('/checkouts/new.html', client_token=client_token, title="Check Out")


@app.route('/checkouts/<transaction_id>', methods=['GET'])
def show_checkout(transaction_id):
    transaction = find_transaction(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('checkouts/show.html', transaction=transaction, result=result, title="Check Out")

@app.route('/checkouts', methods=['POST'])
def checkouts():
    result = transact({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })
    if result.is_success or result.transaction:
        return redirect(url_for('show_checkout', transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: {}: {}'.format(x.code, x.message))
        return redirect(url_for('checkout_new'))
