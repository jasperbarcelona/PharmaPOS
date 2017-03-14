import flask, flask.views
from flask import url_for, request, session, redirect, jsonify, Response, make_response, current_app
from jinja2 import environment, FileSystemLoader
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin, BaseView, expose
from flask import render_template, request
from functools import update_wrapper
from flask import session, redirect
from datetime import timedelta
from datetime import datetime
from sqlalchemy.sql import func
import requests
import datetime
import time
from time import sleep
import json
import uuid
import os

app = flask.Flask(__name__)
db = SQLAlchemy(app)
app.secret_key = '234234rfascasascqweqscasefsdvqwefe2323234dvsv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
# os.environ['DATABASE_URL']
# 'sqlite:///local.db'

ADMIN_URL = 'http://smokadmin.herokuapp.com/sync'
BRANCH = 'Lucena Ravanzo'

DELIVERY_URL = 'http://rcvr.herokuapp.com/transaction/order/info'
DELIVERY_ADD_URL = 'http://rcvr.herokuapp.com/order/add'

WALLET_URL = 'http://127.0.0.1:5000/wallet/info'
TRANSACT_URL = 'http://127.0.0.1:5000/transaction/save'

APP_KEY = '4tqgtah47riyk9475lbmho6847dyth6o'
SCHOOL_NO = 'tmtc-sc2016'

class Serializer(object):
  __public__ = None

  def to_serializable_dict(self):
    dict = {}
    for public_key in self.__public__:
      value = getattr(self, public_key)
      if value:
        dict[public_key] = value
    return dict

class SWEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Serializer):
      return obj.to_serializable_dict()
    if isinstance(obj, (datetime)):
      return obj.isoformat()
    return json.JSONEncoder.default(self, obj)

def SWJsonify(*args, **kwargs):
  return app.response_class(json.dumps(dict(*args, **kwargs), cls=SWEncoder, 
         indent=None if request.is_xhr else 2), mimetype='application/json')
        # from https://github.com/mitsuhiko/flask/blob/master/flask/helpers.py

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    stock = db.Column(db.Float())

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(20))
    description = db.Column(db.String(1000))
    price = db.Column(db.Float())
    markup = db.Column(db.Float())
    flavor_id = db.Column(db.Integer)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    item_name = db.Column(db.String(60))
    date = db.Column(db.String(30))
    qty = db.Column(db.Integer, default=0)
    markup = db.Column(db.Float(), default=0)
    total = db.Column(db.Float(), default=0)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    product_id = db.Column(db.Integer)

class OptionAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    option_id = db.Column(db.Integer)

class ItemAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    consumption_per_order = db.Column(db.Float())
    product_id = db.Column(db.Integer)

class Cashier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    id_no = db.Column(db.String(20))
    password = db.Column(db.String(20))

class Transaction(db.Model, Serializer):
    __public__ = ['id','date','time','cashier_id','total','amount_tendered','change','cashier_name',
                'customer_name','customer_id','status','remarks','payed','note','timestamp','card_no',
                'transaction_type']
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(30))
    time = db.Column(db.String(10))
    cashier_id = db.Column(db.Integer())
    total = db.Column(db.Float())
    amount_tendered = db.Column(db.Float(),default=0)
    change = db.Column(db.Float(),default=0)
    cashier_name = db.Column(db.String(60))
    customer_name = db.Column(db.String(60),default='--')
    customer_id_no = db.Column(db.Integer())
    status = db.Column(db.String(60),default='Pending')
    remarks = db.Column(db.String(60),default='Pending')
    payed = db.Column(db.Boolean())
    note = db.Column(db.Text())
    timestamp = db.Column(db.String(50))
    card_no = db.Column(db.String(20), default='--')
    transaction_type = db.Column(db.String(10))
    sync_status = db.Column(db.String(10),default='failed')

class TransactionItem(db.Model, Serializer):
    __public__ = ['id','transaction_id','item_id','item_name','item_qty','price','done','flavor_id']
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer)
    item_name = db.Column(db.String(100))
    item_qty = db.Column(db.Integer())
    price = db.Column(db.Float())
    done = db.Column(db.Boolean())
    flavor_id = db.Column(db.Integer)

class Loyalty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_no = db.Column(db.String(20))
    status = db.Column(db.String(30),default='Incomplete')
    cheesy = db.Column(db.Boolean(),default=False)
    spicy = db.Column(db.Boolean(),default=False)
    hungarian = db.Column(db.Boolean(),default=False)
    polish = db.Column(db.Boolean(),default=False)
    schublig = db.Column(db.Boolean(),default=False)
    chicken = db.Column(db.Boolean(),default=False)
    beef = db.Column(db.Boolean(),default=False)
    last_used = db.Column(db.String(30))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

class POSAdmin(sqla.ModelView):
    column_display_pk = True
    
admin = Admin(app)
admin.add_view(POSAdmin(Item, db.session))
admin.add_view(POSAdmin(Product, db.session))
admin.add_view(POSAdmin(Cashier, db.session))
admin.add_view(POSAdmin(Transaction, db.session))
admin.add_view(POSAdmin(ItemAllocation, db.session))
admin.add_view(POSAdmin(Option, db.session))
admin.add_view(POSAdmin(OptionAllocation, db.session))
admin.add_view(POSAdmin(TransactionItem, db.session))
admin.add_view(POSAdmin(Sale, db.session))
admin.add_view(POSAdmin(Loyalty, db.session))
admin.add_view(POSAdmin(Category, db.session))

def least_stock(items):
    stock = items[0].stock
    for item in items:
        if item.stock < stock:
            stock = item.stock
    return stock


@app.route('/sync', methods=['GET', 'POST'])
def sync_to_admin():
    sales = Sale.query.filter_by(date=time.strftime("%m / %d / %Y")).all()
    for sale in sales:
        request_body = {
            'date': sale.date,
            'item': sale.item_name,
            'price': sale.markup,
            'qty': sale.qty,
            'total': sale.total,
            'branch': BRANCH
        }
        successful = False
        while not successful:
            try:
                l = requests.post(ADMIN_URL,request_body)
                if l.status_code == 201:
                    successful = True

            except requests.exceptions.ConnectionError as e:
                print 'Could not sync'
                sleep(5)

    return jsonify(status='success',error=None),200


@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('user_id'):
        return redirect('/login')

    if session.get('consumption_items'):
        del(session['consumption_items'])

    sale = Sale.query.filter_by(date=time.strftime("%m / %d / %Y")).first()

    if not sale or sale == None:
        for product_item in Product.query.all():
            sale = Sale(
                item_id = product_item.id,
                item_name = product_item.name,
                date= time.strftime("%m / %d / %Y"),
                markup = product_item.markup,
                )
            db.session.add(sale)
            db.session.commit()
    # else:
    #     for item in sale:
    #         product = Product.query.filter_by(id=item.item_id).first()
    #         item.markup = product.price
    #         db.session.commit()
    #         item.total = item.markup * item.qty
    #         db.session.commit()

    inventory = Item.query.order_by(Item.name).all()
    history = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Transaction.timestamp.desc())
    loyalty = Loyalty.query.all()
    sales = Sale.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Sale.item_name).all()
    cash_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='Cash').all()
    wallet_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='E-Wallet').all()
    total_cash = sum(record.total for record in cash_transactions)
    total_wallet = sum(record.total for record in wallet_transactions)
    sales_total = sum(sale.total for sale in sales)

    categories = Category.query.order_by(Category.name).all()
    products = Product.query.all()

    if session.get('cart_items'):
        return render_template(
            'index.html',
            products=products,
            categories=categories,
            items = session['cart_items'],
            inventory = inventory,
            total = session['total'],
            history = history,
            sales = sales,
            loyalty = loyalty,
            sales_total = sales_total,
            total_cash=total_cash,
            total_wallet=total_wallet,
            date=time.strftime("%m / %d / %Y")
            ), 200

    return render_template(
            'index.html',
            products=products,
            categories=categories,
            inventory = inventory,
            history = history,
            sales = sales,
            loyalty = loyalty,
            sales_total=sales_total,
            total_cash=total_cash,
            total_wallet=total_wallet,
            date=time.strftime("%m / %d / %Y")
            ), 200


@app.route('/consumption/new', methods=['GET', 'POST'])
def new_consumption():
    data = flask.request.form.to_dict()
    item = Item.query.filter_by(id=data['item_id']).first()
    item_name = item.name
    if not session.get('consumption_items'):
        session['consumption_items'] = []
    session['consumption_items'].append({
        'id':data['item_id'],
        'name':item_name,
        'consumption':data['consumption']
        })
    return flask.render_template('new_row.html',items=session['consumption_items'])


@app.route('/consumption/delete', methods=['GET', 'POST'])
def delete_consumption():
    item_id = flask.request.form.get('item_id')

    for item in session['consumption_items']:
        if item['id'] == item_id:
            item_index = session['consumption_items'].index(item)
            del session['consumption_items'][item_index]

    return flask.render_template('new_row.html',items=session['consumption_items'])


@app.route('/consumption/clear', methods=['GET', 'POST'])
def clear_consumption():
    if session.get('consumption_items'):
        del session['consumption_items']
    return flask.render_template('new_row.html',items=[])


@app.route('/products/new', methods=['GET', 'POST'])
def new_product():
    data = flask.request.form.to_dict()

    category = Category.query.filter_by(name=data['category'].title()).first()
    if not category:
        new_category = Category(name=data['category'].title())
        db.session.add(new_category)
        db.session.commit()

    new_product = Product(
        name=data['name'].title(),
        category=data['category'].title(),
        price=data['price'],
        markup=data['markup']
        )
    db.session.add(new_product)
    db.session.commit()

    for item in session['consumption_items']:
        new_allocation = ItemAllocation(
            item_id = item['id'],
            consumption_per_order = item['consumption'],
            product_id = new_product.id
            )
        db.session.add(new_allocation)
        db.session.commit()

    new_sale = Sale(
        item_id = new_product.id,
        item_name = new_product.name,
        date= time.strftime("%m / %d / %Y"),
        markup = new_product.markup,
        )
    db.session.add(new_sale)
    db.session.commit()

    categories = Category.query.order_by(Category.name).all()
    products = Product.query.all()
    return flask.render_template(
        'items.html',
        products=products,
        categories=categories
        )


@app.route('/price/update', methods=['GET', 'POST'])
def update_price():
    rice_meals = Product.query.filter_by(category='Rice Meals').all()
    on_bun = Product.query.filter_by(category='Sausage on Bun').all()
    on_stick = Product.query.filter_by(category='Sausage on Stick').all()

    for item in rice_meals:
        item.price = 65.0
        item.markup = 65.0
        db.session.commit()

    for item in on_bun:
        item.price = 65.0
        item.markup = 65.0
        db.session.commit()

    for item in on_stick:
        item.price = 55.0
        item.markup = 55.0
        db.session.commit()

    return jsonify(status='success',error=''),200


@app.route('/history/search', methods=['GET', 'POST'])
def search_history():
    date = flask.request.form.get('date')

    history = Transaction.query.filter_by(date=date).order_by(Transaction.timestamp.desc())
    cash_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='Cash').all()
    wallet_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='E-Wallet').all()
    total_cash = sum(record.total for record in cash_transactions)
    total_wallet = sum(record.total for record in wallet_transactions)

    return flask.render_template('history.html',history=history,total_cash=total_cash,total_wallet=total_wallet)


@app.route('/sale/search', methods=['GET', 'POST'])
def search_sale():
    date = flask.request.form.get('date')
    sales = Sale.query.filter_by(date=date).order_by(Sale.item_name).all()
    sales_total = sum(sale.total for sale in sales)
    return flask.render_template('sale.html',sales=sales,sales_total=sales_total)


@app.route('/item/search', methods=['GET', 'POST'])
def search_items():
    keyword = flask.request.form.get('keyword')
    if keyword == '':
        categories = Category.query.order_by(Category.name).all()
        products = Product.query.all()
        return flask.render_template(
            'items.html',
            products=products,
            categories=categories
            )
    products = Product.query.filter(Product.name.ilike('%'+keyword+'%')).order_by(Product.name).all()
    return flask.render_template('item_result.html',products=products)


@app.route('/items/new', methods=['GET', 'POST'])
def new_item():
    data = flask.request.form.to_dict()
    item = Item(
        name=data['name'].title(),
        stock=data['stock']
        )
    db.session.add(item)
    db.session.commit()

    inventory = Item.query.order_by(Item.name).all()

    return jsonify( 
    template = flask.render_template('inventory_result.html',inventory=inventory),
    options = flask.render_template('items_select.html',inventory=inventory)
    )


@app.route('/inventory/search', methods=['GET', 'POST'])
def search_inventory():
    keyword = flask.request.form.get('keyword')
    if keyword == '':
        inventory = Item.query.order_by(Item.name).all()
        return flask.render_template('inventory_result.html',inventory=inventory)
    inventory = Item.query.filter(Item.name.ilike('%'+keyword+'%')).order_by(Item.name).all()
    return flask.render_template('inventory_result.html',inventory=inventory)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if session.get('user_id'):
        return redirect('/')
    return flask.render_template('login.html')


@app.route('/authenticate', methods=['GET', 'POST'])
def auth_user():
    data = flask.request.form.to_dict()
    user = Cashier.query.filter_by(id_no=data['username'],password=data['password']).first()
    if not user or user == None:
        return redirect('/login')
    session['user_id'] = user.id
    session['display_name'] = '%s %s' %(user.first_name,user.last_name)
    return redirect('/')


@app.route('/item/qty/get', methods=['GET', 'POST'])
def get_quantity():
    product_id = flask.request.form.get('product_id')
    product = Product.query.filter_by(id=product_id).one()
    session['product_id'] = product_id
    item_ids = ItemAllocation.query.filter_by(product_id=product_id).all()
    options = Option.query.filter_by(product_id=product_id).all()
    items = []
    for item in item_ids:
        items.append(Item.query.filter_by(id=item.item_id).first())

    option_item_ids = []
    for option in options:
        option_item_ids.append(OptionAllocation.query.filter_by(option_id=option.id).all())

    option_items = []
    for option_item in option_item_ids:
        for item in option_item:
            option_items.append(Product.query.filter_by(id=item.item_id).first())

    stock = least_stock(items)

    rice_meals = Product.query.filter_by(category='Rice Meals').order_by(Product.name).all()
    unli_rice_meals = Product.query.filter_by(category='Unli Rice Meals').order_by(Product.name).all()
    sausage_on_stick = Product.query.filter_by(category='Sausage on Stick').order_by(Product.name).all()
    sausage_on_bun = Product.query.filter_by(category='Sausage on Bun').order_by(Product.name).all()
    potato_shit = Product.query.filter_by(category='Potato Shit').order_by(Product.name).all()
    combo_meal = Product.query.filter_by(category='Combo Meal').order_by(Product.name).all()
    drinks = Product.query.filter_by(category='Drinks').order_by(Product.name).all()
    addons = Product.query.filter_by(category='Addons').order_by(Product.name).all()
    others = Product.query.filter_by(category='Others').order_by(Product.name).all()

    return jsonify(
        item_name = product.name,
        item_stock = stock,
        template = flask.render_template('quantity.html', price=product.price,stock=stock,options=options,option_items=option_items,option_item_ids=option_item_ids)
        ),200


@app.route('/item/order/add', methods=['GET', 'POST'])
def order_item():
    product = Product.query.filter_by(id=session['product_id']).one()
    qty = flask.request.form.get('qty')

    sale = Sale.query.filter_by(date=time.strftime("%m / %d / %Y"),item_id=product.id).first()

    sale.qty = int(sale.qty) + int(qty)
    sale.total = sale.qty * sale.markup
    db.session.commit()
        

    options_id = flask.request.form.getlist('options_id[]')
    options_name = flask.request.form.getlist('options_name[]')
    items = []
    item_ids = ItemAllocation.query.filter_by(product_id=product.id).all()
    for item in item_ids:
        items.append(Item.query.filter_by(id=item.item_id).first())

    if options_id:
        for option in options_id:
            option_items = ItemAllocation.query.filter_by(product_id=option).all()
            for item in option_items:
                items.append(Item.query.filter_by(id=item.item_id).first())

    if session.get('cart_items'):
        same_options = False
        for i in session['cart_items']:
            if i['id'] == product.id and i['options'] == options_id and options_id != None:
                current_qty = int(i['quantity']) 
                i['quantity'] = current_qty + int(qty)
                i['price'] += float(qty) * product.price
                same_options = True
                for item in items:
                    allocation = ItemAllocation.query.filter_by(item_id=item.id,product_id=product.id).first()
                    if allocation:
                        item.stock -= (float(qty) * allocation.consumption_per_order)
                    else:
                        item.stock -= float(qty)
                db.session.commit()
                break
        if same_options == False:
            existing = False
            for i in session['cart_items']:
                if i['id'] == product.id and i['options'] == options_id:
                    current_qty = float(i['quantity']) 
                    i['quantity'] = current_qty + float(qty)
                    i['price'] += float(qty) * product.price
                    existing = True
                    for item in items:
                        allocation = ItemAllocation.query.filter_by(item_id=item.id,product_id=product.id).first()
                        if allocation:
                            item.stock -= (float(qty) * allocation.consumption_per_order)
                        else:
                            item.stock -= float(qty)
                        db.session.commit()
                    break
            if not existing:
                session['cart_items'].append({
                    "id":product.id,
                    "name":'%s' % product.name,
                    "options":options_id,
                    "quantity":qty,
                    "flavor_id":product.flavor_id,
                    "price":product.price * float(qty)
                    })
                for item in items:
                    allocation = ItemAllocation.query.filter_by(item_id=item.id,product_id=product.id).first()
                    if allocation:
                        item.stock -= (float(qty) * allocation.consumption_per_order)
                    else:
                        item.stock -= float(qty)
                db.session.commit()
    else:
        session['cart_items'] = [{
                "id":product.id,
                "name":'%s' % product.name,
                "options":options_id,
                "quantity":qty,
                "flavor_id":product.flavor_id,
                "price":product.price * float(qty)
                }]
        for item in items:
            allocation = ItemAllocation.query.filter_by(item_id=item.id,product_id=product.id).first()
            if allocation:
                item.stock -= (float(qty) * allocation.consumption_per_order)
            else:
                item.stock -= float(qty)
        db.session.commit()

    session['total'] = 0
    for i in session['cart_items']:
        session['total'] += i['price']

    inventory = Item.query.order_by(Item.name).all()
    sales = Sale.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Sale.item_name).all()
    sales_total = sum(sale.total for sale in sales)
    return jsonify(
        transaction_template=flask.render_template('transaction.html',items=session['cart_items'], total=session['total']),
        inventory_template=flask.render_template('inventory.html',inventory=inventory),
        sales_template=flask.render_template('sale.html',sales=sales, sales_total=sales_total)
        ) 


@app.route('/item/delete/get', methods=['GET', 'POST'])
def get_item_to_delete():
    product_id = flask.request.form.get('product_id')
    product = Product.query.filter_by(id=product_id).one()
    session['delete_id'] = product_id
    return jsonify(
        product_name = product.name
        ),200


@app.route('/transaction/item/delete/get', methods=['GET', 'POST'])
def get_item_to_delete_transaction():
    product_id = flask.request.form.get('product_id')
    product = TransactionItem.query.filter_by(id=product_id).one()
    session['delete_id'] = product_id
    return jsonify(
        product_name = product.item_name
        ),200


@app.route('/transaction/cancel', methods=['GET', 'POST'])
def cancel_transaction():
    if session.get('cart_items'):
        del(session['cart_items'])
    return flask.render_template('transaction.html')


@app.route('/item/delete', methods=['GET', 'POST'])
def delete_item_from_order():
    product = Product.query.filter_by(id=session['delete_id']).one()
    items = []
    item_ids = ItemAllocation.query.filter_by(product_id=product.id).all()
    for item in item_ids:
        items.append(Item.query.filter_by(id=item.item_id).first())

    for i in session['cart_items']:
        if i['id'] == product.id:
            sale = Sale.query.filter_by(date=time.strftime("%m / %d / %Y"),item_id=product.id).first()
            sale.qty = int(sale.qty) - int(i['quantity'])
            sale.total = sale.qty * sale.markup
            db.session.commit()

            if i['options'] != None:
                for option in i['options']:
                    option_items = ItemAllocation.query.filter_by(product_id=option).all()
                    for item in option_items:
                        items.append(Item.query.filter_by(id=item.item_id).first())
            for item in items:
                allocation = ItemAllocation.query.filter_by(item_id=item.id,product_id=product.id).first()
                if allocation:
                    item.stock += (float(i['quantity']) * allocation.consumption_per_order)
                else:
                    item.stock += float(i['quantity'])
            db.session.commit()
            item_index = session['cart_items'].index(i)
            del session['cart_items'][item_index]
            break

    session['total'] = 0
    for i in session['cart_items']:
        session['total'] += i['price']   

    inventory = Item.query.order_by(Item.name).all()
    sales = Sale.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Sale.item_name).all()
    sales_total = sum(sale.total for sale in sales)
    return jsonify(
        item_count = len(session['cart_items']),
        transaction_template=flask.render_template('transaction.html',items=session['cart_items'], total=session['total']),
        inventory_template=flask.render_template('inventory.html',inventory=inventory),
        sales_template=flask.render_template('sale.html',sales=sales,sales_total=sales_total)
        )


@app.route('/transaction/existing', methods=['GET', 'POST'])
def get_existing_transactions():
    existing = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),payed=False).order_by(Transaction.timestamp.desc()).all()
    return flask.render_template('existing.html',existing=existing)


@app.route('/loyalty/points', methods=['GET', 'POST'])
def show_points():
    card_id = flask.request.form.get('id')
    points = Loyalty.query.filter_by(id=card_id).first()
    return jsonify(
        template=flask.render_template('points.html',points=points),
        card_no=points.card_no
        )


@app.route('/item/adjust/get', methods=['GET', 'POST'])
def get_item_to_adjust():
    item_id = flask.request.form.get('item_id')
    item = Item.query.filter_by(id=item_id).first()
    session['adjust_id'] = item_id
    return jsonify(
        current_stock=item.stock,
        item_name=item.name
        ),200


@app.route('/item/delete', methods=['GET', 'POST'])
def delete_item():
    item = Item.query.filter_by(id=session['adjust_id']).first()
    db.delete(item)
    db.session.commit()
    inventory = Item.query.order_by(Item.name).all()
    return jsonify(
        status='success',
        error=None,
        inventory_template=flask.render_template('inventory.html',inventory=inventory)
        ),201


@app.route('/item/adjust', methods=['GET', 'POST'])
def adjust_item():
    item = Item.query.filter_by(id=session['adjust_id']).first()
    data = flask.request.form.to_dict()
    item.stock += float(data['plus']) - float(data['minus'])
    db.session.commit()
    return jsonify(
        status='success',
        error=None,
        item_id=item.id,
        new_stock=item.stock
        ),201


@app.route('/transaction/cash/amount', methods=['GET', 'POST'])
def get_amount_tendered():
    return jsonify(total=session['total']),200


@app.route('/transaction/id/save', methods=['GET', 'POST'])
def save_transaction_id():
    transaction_id = flask.request.form.get('id')
    session['transaction_id'] = transaction_id
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    return jsonify(
        customer_name=transaction.customer_name,
        total=session['total']
        ),200


@app.route('/transaction/void/id', methods=['GET', 'POST'])
def void_id():
    session['void_id'] = flask.request.form.get('id')
    return jsonify(
        status='success',
        error=''
        ),200


@app.route('/transaction/history/get', methods=['GET', 'POST'])
def get_history():
    history = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Transaction.timestamp.desc())
    cash_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='Cash').all()
    wallet_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='E-Wallet').all()
    total_cash = sum(record.total for record in cash_transactions)
    total_wallet = sum(record.total for record in wallet_transactions)
    return jsonify(
        status='success',
        error='',
        history_template=flask.render_template('history.html',history=history,total_cash=total_cash,total_wallet=total_wallet)
        ),201


@app.route('/transaction/later/amount', methods=['GET', 'POST'])
def get_amount_tendered_later():
    transaction_id = flask.request.form.get('id')
    session['transaction_id'] = transaction_id
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    return jsonify(total=transaction.total),200


@app.route('/transaction/finish/cash', methods=['GET', 'POST'])
def finish_transaction():
    tendered = flask.request.form.get('tendered')
    transaction = Transaction(
        date = time.strftime("%m / %d / %Y"),
        time = time.strftime("%-I:%M %p"),
        cashier_id = session['user_id'],
        cashier_name = session['display_name'],
        total=session['total'],
        amount_tendered=tendered,
        change=float(tendered) - float(session['total']),
        payed=True,
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f'),
        transaction_type='Cash'
        )
    db.session.add(transaction)
    db.session.commit()

    items = []
    for item in session['cart_items']:
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            item_id=item['id'],
            item_name=item['name'],
            item_qty=item['quantity'],
            price=item['price'],
            flavor_id=item['flavor_id'],
            done=False
        )
        db.session.add(transaction_item)

        items.append({
            'transaction_id': transaction.id,
            'item_id': item['id'],
            'item_name': item['name'],
            'item_qty': item['quantity'],
            'price': item['price'],
            'flavor_id': item['flavor_id'],
            'done': True
            })

    db.session.commit()
    session['cart_items'] = []
    history = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Transaction.timestamp.desc())
    cash_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='Cash').all()
    wallet_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='E-Wallet').all()
    total_cash = sum(record.total for record in cash_transactions)
    total_wallet = sum(record.total for record in wallet_transactions)

    data = {
        'transaction_id': transaction.id,
        'school_no': SCHOOL_NO,
        'date': transaction.date,
        'time': transaction.time,
        'cashier_id': transaction.cashier_id,
        'cashier_name': transaction.cashier_name,
        'total': transaction.total,
        'amount_tendered': transaction.amount_tendered,
        'change': transaction.change,
        'payed': transaction.payed,
        'timestamp': transaction.timestamp,
        'transaction_type': transaction.transaction_type,
        'items':items
        }

    try:
        l = requests.post(TRANSACT_URL,json=data,params={'id_no':session['wallet'],'app_key':APP_KEY})
        if l.status_code == 201:
            transaction.sync_status = 'successful'
            db.session.commit()

    except requests.exceptions.ConnectionError as e:
        print 'failed to sync'

    return jsonify(
        status='success',
        error='',
        transaction_template=flask.render_template('no_transaction.html'),
        history_template=flask.render_template('history.html',history=history,total_cash=total_cash,total_wallet=total_wallet)
        ),201


@app.route('/ewallet/info', methods=['GET', 'POST'])
def get_ewallet_info():
    id_no = flask.request.form.get('id_no')
    session['wallet'] = id_no
    try:
        l = requests.post(WALLET_URL,params={'id_no':id_no,'app_key':APP_KEY})
        if l.status_code == 200:
            session['customer_name'] = l.json()['student_name']
            return jsonify(
            status = 'success',
            template = flask.render_template(
                'wallet_info.html',
                success=True,
                student_name=l.json()['student_name'],
                credits=l.json()['credits']
                ),
            student_name=l.json()['student_name'],
            credits=l.json()['credits']
            )
        else:
            return jsonify(
            status = 'failed',
            template = flask.render_template(
                'wallet_info.html',
                success=False,
                message=l.json()['message']
                )
            )

    except requests.exceptions.ConnectionError as e:
        return jsonify(
            status = 'failed',
            template = flask.render_template(
                'wallet_info.html',
                success=False,
                message='Could not connect to server'
                )
            )


@app.route('/transaction/finish/wallet', methods=['GET', 'POST'])
def finish_transaction_wallet():
    transaction = Transaction(
        date = time.strftime("%m / %d / %Y"),
        time = time.strftime("%-I:%M %p"),
        cashier_id = session['user_id'],
        cashier_name = session['display_name'],
        customer_name = session['customer_name'],
        customer_id_no = session['wallet'],
        total=session['total'],
        payed=True,
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f'),
        transaction_type='E-Wallet'
        )
    db.session.add(transaction)
    db.session.commit()

    items = []
    for item in session['cart_items']:
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            item_id=item['id'],
            item_name=item['name'],
            item_qty=item['quantity'],
            price=item['price'],
            flavor_id=item['flavor_id'],
            done=True
        )
        db.session.add(transaction_item)

        items.append({
            'transaction_id': transaction.id,
            'item_id': item['id'],
            'item_name': item['name'],
            'item_qty': item['quantity'],
            'price': item['price'],
            'flavor_id': item['flavor_id'],
            'done': True
            })

    db.session.commit()

    session['cart_items'] = []

    history = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y")).order_by(Transaction.timestamp.desc())
    cash_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='Cash').all()
    wallet_transactions = Transaction.query.filter_by(date=time.strftime("%m / %d / %Y"),transaction_type='E-Wallet').all()
    total_cash = sum(record.total for record in cash_transactions)
    total_wallet = sum(record.total for record in wallet_transactions)

    data = {
        'transaction_id': transaction.id,
        'school_no': SCHOOL_NO,
        'date': transaction.date,
        'time': transaction.time,
        'cashier_id': transaction.cashier_id,
        'cashier_name': transaction.cashier_name,
        'customer_name': transaction.customer_name,
        'customer_id_no': transaction.customer_id_no,
        'total': transaction.total,
        'payed': transaction.payed,
        'timestamp': transaction.timestamp,
        'transaction_type': transaction.transaction_type,
        'items':items
        }

    try:
        l = requests.post(TRANSACT_URL,json=data,params={'id_no':session['wallet'],'app_key':APP_KEY})
        if l.status_code == 201:
            transaction.sync_status = 'successful'
            db.session.commit()

    except requests.exceptions.ConnectionError as e:
        print 'failed to sync'

    return jsonify(
            status='success',
            transaction_template=flask.render_template('no_transaction.html'),
            history_template=flask.render_template('history.html',history=history,total_cash=total_cash,total_wallet=total_wallet)
            ),201


@app.route('/order/list', methods=['GET', 'POST'])
def order_list():
    orders = Transaction.query.filter_by(status='Pending').order_by(Transaction.timestamp).all()
    items = []
    for order in orders:
        items.append(TransactionItem.query.filter_by(transaction_id=order.id).all())
    return flask.render_template('orders.html', orders=orders,items=items)


@app.route('/order/list/update', methods=['GET', 'POST'])
def update_list():
    orders = Transaction.query.filter_by(status='Pending').order_by(Transaction.timestamp).all()
    items = []
    for order in orders:
        items.append(TransactionItem.query.filter_by(transaction_id=order.id).all())
    return flask.render_template('orders_update.html', orders=orders,items=items)


@app.route('/order/status/update', methods=['GET', 'POST'])
def update_order_status():
    data = flask.request.form.to_dict()
    order = Transaction.query.filter_by(id=data['id']).first()
    items = TransactionItem.query.filter_by(transaction_id=order.id).all()
    order.remarks = data['status']
    if data['status'] == 'Done':  
        order.status = 'Done'
        for item in items:
            item.done = True
    db.session.commit()

    return redirect('/order/list/update')


@app.route('/loyalty/use', methods=['GET', 'POST'])
def use_loyalty_card():
    card_no = flask.request.form.get('card_no')
    products = TransactionItem.query.filter_by(transaction_id=session['transaction_id']).all()

    transaction = Transaction.query.filter_by(id=session['transaction_id']).first()
    transaction.card_no = card_no
    db.session.commit()

    loyalty = Loyalty.query.filter_by(card_no=card_no).first()
    if not loyalty or loyalty == None:
        loyalty = Loyalty(
            card_no=card_no
            )
        db.session.add(loyalty)
        db.session.commit()

    for product in products:
        if product.flavor_id == 1:
            loyalty.cheesy = True
        
        elif product.flavor_id == 2:
            loyalty.spicy = True

        elif product.flavor_id == 3:
            loyalty.hungarian = True
        
        elif product.flavor_id == 4:
            loyalty.polish = True

        elif product.flavor_id == 5:
            loyalty.schublig = True

        elif product.flavor_id == 6:
            loyalty.chicken = True

        elif product.flavor_id == 7:
            loyalty.beef = True

    loyalty.last_used = time.strftime("%m / %d / %Y")

    if loyalty.cheesy == True and loyalty.spicy == True\
    and loyalty.hungarian == True and loyalty.polish == True\
    and loyalty.schublig == True and loyalty.chicken == True\
    and loyalty.beef == True:
        loyalty.status="Complete"

    db.session.commit()

    return '',200


@app.route('/transaction/info', methods=['GET', 'POST'])
def get_transaction_info():
    transaction_id = flask.request.form.get('id')
    session['transaction_id'] = transaction_id
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    items = TransactionItem.query.filter_by(transaction_id=transaction_id).all()
    return flask.render_template('transaction_info.html',transaction=transaction,items=items)


@app.route('/session/clear', methods=['GET', 'POST'])
def clear_session():
    session.clear()
    return jsonify(status='success'),200



@app.route('/sauce/create', methods=['GET', 'POST'])
def create_sauce_allocation():
    for i in range(41):
        catsup = OptionAllocation(
            item_id=52,
            option_id=i+8
            )
        mustard = OptionAllocation(
            item_id=53,
            option_id=i+8
            )
        mixed = OptionAllocation(
            item_id=54,
            option_id=i+8
            )

        db.session.add(catsup)
        db.session.add(mustard)
        db.session.add(mixed)
        db.session.commit()

    return 'done'


@app.route('/drinks/create', methods=['GET', 'POST'])
def create_drink_allocation():
    for i in range(8):
        iced_tea = OptionAllocation(
            item_id=44,
            option_id=i+1
            )
        juice = OptionAllocation(
            item_id=45,
            option_id=i+1
            )

        db.session.add(iced_tea)
        db.session.add(juice)
        db.session.commit()

    return 'done'


@app.route('/db/update', methods=['GET', 'POST'])
def update_database():
    items = Item.query.all()
    products = Product.query.all()
    item_allocation = ItemAllocation.query.all()
    options = Option.query.all()
    option_allocation = OptionAllocation.query.all()

    db.drop_all()
    db.create_all()

    for item in items:
        add_item = Item(
            name = item.name,
            stock = item.stock
            )
        db.session.add(add_item)

    for product in products:
        add_prod = Product(
            name=product.name,
            category=product.category,
            description=product.description,
            price=product.price
            )
        db.session.add(add_prod)

    for alloc in item_allocation:
        add_alloc = ItemAllocation(
            product_id=alloc.product_id,
            item_id=alloc.item_id,
            consumption_per_order=alloc.consumption_per_order,
            )
        db.session.add(add_alloc)

    for option in options:
        add_option = Option(
            name=option.name,
            product_id=option.product_id
            )
        db.session.add(add_option)

    for option_alloc in option_allocation:
        allocation = OptionAllocation(
            item_id=option_alloc.item_id,
            option_id=option_alloc.option_id
            )
        db.session.add(option_alloc)

    db.session.commit()
    return jsonify(status='success'), 201


@app.route('/db/rebuild', methods=['GET', 'POST'])
def rebuild_database():
    db.drop_all()
    db.create_all()

    cashier = Cashier(
        first_name='Jasper',
        last_name='Barcelona',
        id_no='2011334281',
        password='jasperbarcelona'
        )
    db.session.add(cashier)
    db.session.commit()

    return jsonify(status='success'), 201


if __name__ == '__main__':
    app.debug = True
    app.run(port=8000)
    # host='192.168.2.44',port=80