from datetime import datetime,timedelta 

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from bson.objectid import ObjectId
from flask_paginate import Pagination, get_page_parameter

import pymongo, requests, json


import re

from dbcon import (db, sauda_, get_expiry,
    add_purchase, add_sales, addinform, get_comp, profitformonth,
    get_sales, get_variety, getTodaysPurchaserRecords, getTodaysSaleRecords,
    sform, addnewform, update_inventory, add_item, getOutOfStock, searchform,
    get_purchase, get_productname, getQuantityFromWh, getSalesOf6Months, inventoryfunc)

# from flask.ext.paginate import Pagination
# page, per_page, offset = get_page_items()  

app = Flask(__name__)
app.secret_key = 'loginner'

users = {'admin' : 'pass!@#$admin',
        'vimal'   : 'hemnani!@#'}

notadmin = {
    'userprofile': 'profile',
}
# @app.route('/')
# def main():
#     return render_template(url_for('expenses'))



@app.route("/paid" , methods=['POST','GET'])
def paid():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = searchform()
    arr= None
    expenses_ = db.expense.aggregate([ { '$group': { '_id': None, 'tot': { '$sum': '$Amount' } } } ])
    expenses = 0
    for i in expenses_:
        expenses = i['tot']
    arr = db.purchase.find({"amount_paid" : {"$gt" : 0 } })
    if (request.method == 'POST'):
        cursor = None
        name = re.compile(r''+request.form['name1'], re.I)
        phone = re.compile(r''+request.form['phone'], re.I)
        fromdate = request.form['from']
        todate = request.form['to']

        if fromdate!='' and todate!='':
            q = {'amount_paid': {'$gt': 0}, 
            'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}, 
            'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y')) }
                }
            expenses_ = db.expense.aggregate([ {'$match': {'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y'))} } },
                { '$group': { '_id': None, 'tot': { '$sum': '$Amount' } } } ])
    
            for i in expenses_:
                expenses = i['tot']           
        else:
            q = {'amount_paid': {'$gte': 0}, 
            'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}
            }
            expenses = expenses

        name = 'Total Bill for ' + request.form['name1'] 
        total = db.purchase.aggregate([ { '$match' : q },
            { '$group': { '_id': None, 'tot': { '$sum': '$Total' } } } ])
        for i in total:
            total = i['tot']
        cursor = db.purchase.find(q)
        return render_template('accountspaid.html', arr=cursor, but_action = "Pay", expenses = expenses, name=name, total = total,
        form=form, heading = 'Accounts '+'Paid', redirect = redirect)

    return render_template('accountspaid.html', arr=arr, but_action = "Pay",expenses = expenses, name=None, total = None,
     form=form, heading = 'Accounts '+'Paid', redirect = redirect)

@app.route("/recieved" , methods=['POST','GET'])
def recieved():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = searchform()
    arr= None
        
    arr = db.sales.find({"amount_paid" : {"$gt" : 0 } })
    if (request.method == 'POST'):
        cursor = None
        name = re.compile(r''+request.form['name1'], re.I)
        phone = re.compile(r''+request.form['phone'], re.I)
        fromdate = request.form['from']
        todate = request.form['to']

        if fromdate!='' and todate!='':
            q = {'amount_paid': {'$gt': 0}, 
            'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}, 
            'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y')) }
                }
                     
        else:
            q = {'amount_paid': {'$gte': 0}, 
            'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}
            }

        name = 'Total Bill for ' + request.form['name1']
        if fromdate!='' and todate!='':
            name = ' ' + name + 'Date: ' + fromdate + ' To ' + todate   
        total = db.sales.aggregate([ { '$match' : q },
            { '$group': { '_id': None, 'tot': { '$sum': '$Total' } } } ])
        for i in total:
            total = i['tot']
        cursor = db.sales.find(q)
        return render_template('accountspaid.html', arr=cursor, but_action = "Recieve", expenses = None, name=name, total = total,
        form=form, heading = 'Accounts '+'Recieved', redirect = redirect)

    return render_template('accountspaid.html', arr=arr, but_action = "Recieve",expenses = None, name=None, total = None,
     form=form, heading = 'Accounts '+'Recieved', redirect = redirect)

@app.route("/expenses" , methods=['Post','GET'])
def expenses():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    search = False

    page = request.args.get(get_page_parameter(), type=int, default=1)
    skip = ((page-1)*10)
    users = db.expense.find().sort([('Date',pymongo.DESCENDING)]).skip(skip).limit(10)
    pagination = Pagination(page=page, total=users.count(), search=search, record_name='Expenses', css_framework='bootstrap4')
    if request.form.get('Add Expense') == 'Add Expense':
        dict_ = {
            "Amount": int(request.form['amount']),
            "Description": request.form['Description'],
            "Date": datetime.strptime(request.form['date'], '%m/%d/%Y')
            }
        db.expense.insert(dict_)
        return redirect(url_for('expenses'))
    
    if (request.form.get('Search') == 'Search'):
        description = re.compile(r''+request.form['description'], re.I)
        amount = request.form['amount']
        if amount!='':
            querry = {"Description": {'$regex': description}, "Amount": int(amount)}
        else:
            querry = {"Description": {'$regex': description}}
        page = request.args.get(get_page_parameter(), type=int, default=1)
        skip = ((page-1)*10)
        users = db.expense.find(querry).sort([('Date',pymongo.DESCENDING)])
        pagination = Pagination(page=page, total=users.count(), search=search, record_name='Expenses', css_framework='bootstrap4')


        return render_template('expenses.html', arr=users, redirect = redirect, pagination=pagination)

    return render_template('expenses.html', arr=users, redirect = redirect, pagination=pagination)

@app.route("/account" , methods=['Post','GET'])
def account():
    if not session.get('logged_in'):
        if not session.get('notadmin'):
            return redirect(url_for('login'))
    form = searchform()
    form.transaction.choices = [('Payable','Payable'), ('Recievable','Recievable')]
    form.transaction.label = "Select Accounts"

    su = db.sales.aggregate([ { '$match': { 'transaction': "Credit" } },
        { '$group': { '_id': None, 'tot': { '$sum': '$amount_remaining' } } } ])
    credits = 0
    for i in su:
        credits = (i['tot'])

    creditors = db.sales.count_documents({ 'transaction': "Credit" })
    debitors = db.purchase.count_documents({ 'transaction': "Credit" })

    su = db.purchase.aggregate([ { '$match': { 'transaction': "Credit" } },
        { '$group': { '_id': None, 'tot': { '$sum': '$amount_remaining' } } } ])
    debts = 0
    for i in su:
        debts = (i['tot'])

    if request.method == 'POST':
        name = re.compile(r''+request.form['name1'], re.I)
        phone = re.compile(r''+request.form['phone'], re.I)
        fromdate = request.form['from']
        todate = request.form['to']

        if form.transaction.data == "Recievable":
            if fromdate!='' and todate!='':
                q = {'Name': {'$regex': name}, 
                'Phone': {'$regex': phone}, 
                "transaction" : "Credit",
                'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y')) }
                    }
                        
            else:
                q = {'Name': {'$regex': name}, 
                'Phone': {'$regex': phone},
                "transaction" : "Credit"}

            su = db.sales.aggregate([ { '$match': q},
                { '$group': { '_id': None, 'tot': { '$sum': '$amount_remaining' } } } ])
            credits = 0
            for i in su:
                credits = (i['tot'])

            creditors = db.sales.count_documents(q)
            debitors = db.purchase.count_documents(q)

            su = db.purchase.aggregate([ { '$match': q },
                { '$group': { '_id': None, 'tot': { '$sum': '$amount_remaining' } } } ])
            debts = 0
            for i in su:
                debts = (i['tot'])

            return render_template('account.html', arr=db.sales.find(q), form=form, but_action = "Recieve", credit_amount = credits, debt_amount = debts,
            heading = 'Accounts '+   (form.transaction.data), redirect = redirect, creditors = creditors, debitors = debitors)
        if form.transaction.data == "Payable":
            if fromdate!='' and todate!='':
                q = {'Name': {'$regex': name}, 
                'Phone': {'$regex': phone}, 
                "transaction" : "Credit",
                'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y')) }
                    }
                        
            else:
                q = {'Name': {'$regex': name}, 
                'Phone': {'$regex': phone},
                "transaction" : "Credit"}

            su = db.sales.aggregate([ { '$match': q},
                { '$group': { '_id': None, 'tot': { '$sum': '$amount_remaining' } } } ])
            credits = 0
            for i in su:
                credits = (i['tot'])

            creditors = db.sales.count_documents(q)
            debitors = db.purchase.count_documents(q)

            su = db.purchase.aggregate([ { '$match': q },
                { '$group': { '_id': None, 'tot': { '$sum': '$amount_remaining' } } } ])
            debts = 0
            for i in su:
                debts = (i['tot'])


            return render_template('account.html', arr=db.purchase.find(q), but_action = "Pay", credit_amount = credits, debt_amount = debts,
            form=form, heading = 'Accounts '+(form.transaction.data), redirect = redirect, creditors = creditors, debitors = debitors)

    return render_template('account.html', arr=db.sales.find({"transaction" : "Credit"}), but_action = "Recieve", credit_amount = credits, debt_amount = debts,
     form=form, heading = 'Accounts '+'Recievable', redirect = redirect, creditors = creditors, debitors = debitors)

@app.route('/login') 
def loginform():
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password and username in users and users[username] == password:
        session['logged_in'] = True
        return redirect(url_for('home'))

    elif username and password and username in notadmin and notadmin[username] == password:
        session['notadmin'] = True
        return redirect(url_for('inventory'))

    return render_template('index.html')

@app.route("/home")
def home():

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    values, profit = getQuantityFromWh()
    labels = ['Sales', 'Purchases', 'Expenses']
    colors = ["#32CD32", "#FF0000", "#FFFF00"]
    (bar_labels, bar_values) = getSalesOf6Months()
    max2 = max(bar_values)
    outofstock = getOutOfStock(100)
    a = db.sales.aggregate([{'$group' : {'_id' : '$Productname', "count" : {'$sum' : '$Quantity'}}},{'$sort' : {"count" : -1}}, {'$limit' : 5}])
    products=[]
    for i in a:
        products.append((i['_id'], i['count']))
    a = db.inventory.aggregate([ { '$group': { '_id': None, 'tot': { '$sum': {'$multiply': [ '$PriceperKG', '$Quantity'] } } } } ])
    for i in a:
        tot = (i['tot'])
    date = datetime.strptime("01/"+ (datetime.today().strftime('%m/%Y')) , "%m/%d/%Y")

    a = db.expense.aggregate([ {'$match': {'Date': {'$gte': date}}}, { '$group' : { '_id': None, 'tot': { '$sum': '$Amount' } } }  ])
    ex = 0
    for i in a:
        ex = i['tot']

    a= db.sales.aggregate([{'$match': { 'amount_remaining': { '$gt': 0 } }},
                    {'$group' : {'_id' : '$Name', "count" : {'$sum' : '$amount_remaining'}}},
                    {'$sort' : {"count" : -1}}, {'$limit' : 5}])
    creditss=[]
    for i in a:
        creditss.append((i['_id'], i['count']))


    return render_template('home.html', max=17000, 
    set = zip(values, labels, colors ), profit = profit, max2 = max2, labels=bar_labels, values=bar_values, products = products, ex = ex, month_profit = profitformonth(date),
    creditss=creditss,  total_inventory=tot)

@app.route("/inventory", methods=['Post','GET'])
def inventory():
    if not session.get('logged_in'):
        if not session.get('notadmin'):
            return redirect(url_for('login'))
    page = request.args.get(get_page_parameter(), type=int, default=1)
    search = False
    skip = ((page-1)*10)
    arr = db.inventory.find().skip(skip).limit(10)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=arr.count(), search=search, record_name='Inventory', css_framework='bootstrap4')

    if request.method == 'POST':
        # if (request.form.get('Search') == 'Search'):
        product = re.compile(r''+request.form['Product'], re.I)
        variety = re.compile(r''+request.form['Variety'], re.I)
        brand = re.compile(r''+request.form['Brand'], re.I)
        querry = {"Productname": {'$regex': product}, 
                "Variety": {'$regex': variety},
                "Brand":  {'$regex': brand} }
        print(querry)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        skip = ((page-1)*10)
        users = db.inventory.find(querry).sort([('Date',pymongo.DESCENDING)])
        pagination = Pagination(page=page, total=users.count(), search=search, record_name='Expenses', css_framework='bootstrap4')


        return render_template('inventory.html', arr=users, redirect = redirect, pagination=pagination)

    return render_template('inventory.html', arr=arr, redirect = redirect, pagination=pagination)

@app.route("/sales"  , methods=['Post','GET'])
def sales():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = searchform()

    if request.method == 'POST':
        name = re.compile(r''+request.form['name1'], re.I)
        phone = re.compile(r''+request.form['phone'], re.I)
        fromdate = request.form['from']
        todate = request.form['to']
        if fromdate!='' and todate!='':
            q = {'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}, 
            'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y')) }
                }
                    
        else:
            q = {'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}}



        return render_template('sales.html', arr=get_sales(q), form=form, redirect = redirect)
    return render_template('sales.html', arr=get_sales(), form=form, redirect = redirect)

@app.route("/sauda"  , methods=['POST','GET'])
def sauda():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = sform()
    form2 = sform() 
    
    search = False

    page = request.args.get(get_page_parameter(), type=int, default=1)
    skip = ((page-1)*10)
    users = db.sauda.find().sort([('Date',pymongo.DESCENDING)]).skip(skip).limit(10)
    pagination = Pagination(page=page, total=users.count(), search=search, record_name='Expenses', css_framework='bootstrap4')
    if (request.form.get('Add Sauda') == 'Add Sauda'):
        _sauda = {"Name":form.name.data,
        "Phone":str(form.phone.data),
        "country":form.country.data,
        "Company": form.c_comp.data,
        "Description": form.description.data,
        "Date": datetime.strptime(request.form['date'], '%m/%d/%Y')}
        db.sauda.insert(_sauda)
        _sauda = None   
        return redirect(url_for('sauda'))
    if (request.form.get('Search') == 'Search'):
        name = re.compile(r''+request.form['name1'], re.I)
        phone = re.compile(r''+request.form['phone'], re.I)
        company = re.compile(r''+request.form['company'], re.I)
        _sauda = {"Name": {'$regex': name},
                "Phone": {'$regex': phone},
                "Company": {'$regex': company}}

        return render_template('sauda.html', arr=db.sauda.find(_sauda).sort([('Date',pymongo.DESCENDING)]), form=form, form2=form2, redirect = redirect, pagination=pagination)
    return render_template('sauda.html', arr=users, form=form, form2=form2, redirect = redirect, pagination=pagination)

@app.route("/addinventory" , methods=['Post','GET'])
def addinventory():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    form = addinform()
    form.product.choices = get_productname()
    form_addnew =  addnewform()   
    if (request.form.get('Submit') == 'Add Item') and form_addnew.validate_on_submit:
        purchase = {"Productname":form_addnew.product.data,
                   "Variety": form_addnew.variety.data,
                   "Brand":form_addnew.Brand.data,
                    "Name": form_addnew.name.data,
                    "country": form_addnew.country.data,
                    "Phone": str(form_addnew.phone.data),
                    "Company": form_addnew.c_comp.data,
                    "Quantity": float(form_addnew.quan.data),
                    "Total": form_addnew.price.data,
                    "PriceperKG": int(form_addnew.priceperkg.data),
                    "expiry": datetime.strptime(request.form['expiry'], '%m/%d/%Y'),
                    "manufacture": datetime.strptime(request.form['manufacture'], '%m/%d/%Y'),
                    "transaction" : form_addnew.transaction.data,
                    "Date": datetime.strptime(request.form['date'], '%m/%d/%Y'),
                    'Description': [] }

        dicts = {
                "Productname" : form_addnew.product.data, 
                 "Variety"     : form_addnew.variety.data, 
                 "Brand"       : form_addnew.Brand.data, 
                 "Quantity"    : float(form_addnew.quan.data),
                 "Total": form_addnew.price.data,
                 "PriceperKG": form_addnew.priceperkg.data,
                 "expiry": datetime.strptime(request.form['expiry'], '%m/%d/%Y'),
                 "manufacture": datetime.strptime(request.form['manufacture'], '%m/%d/%Y'),
                 "Date" : datetime.now()
                 }

        if form_addnew.transaction.data =='Credit':
            purchase['amount_remaining'] = purchase['Total']
            purchase['amount_paid'] = 0

        if form_addnew.transaction.data =='Cash':
            purchase['amount_remaining'] = 0
            purchase['amount_paid'] = purchase['Total']

        if add_item(dicts) and add_purchase(purchase):
            flash("Purchase Record Created and added item in inventory.!!!", 'Success')
            return redirect(url_for('addinventory'))
        else:
            flash("There was an Error.!!!", 'ERROR')

    return render_template('addinventory.html', form = form, form_addnew = form_addnew)

@app.route("/salesform" , methods=['Post','GET'])
def salesform():
    if not session.get('logged_in'):
        if not session.get('notadmin'):
            return redirect(url_for('login'))

    form = sform()
    form.product.choices = get_productname()    
    if request.method == 'POST':
        _sale = {"Name":form.name.data,
                "Productname":form.product.data,
                "country": form.country.data,
                "Quantity": float(form.quan.data),
                "Brand":form.Brand.data,
                "Variety": form.variety.data,
                "Company": form.c_comp.data,
                "Phone": str(form.phone.data),
                "Total" : form.price.data,
                "transaction" : form.transaction.data,
                "Date": datetime.strptime(request.form['date'], '%m/%d/%Y'),
                'Description': [] }

        if form.transaction.data =='Credit':
            _sale['amount_remaining'] = _sale['Total']
            _sale['amount_paid'] = 0

        if form.transaction.data =='Cash':
            _sale['amount_remaining'] = 0
            _sale['amount_paid'] = _sale['Total']

        if update_inventory(form.product.data,form.variety.data,form.Brand.data, float(form.quan.data), form.expiry.data):
            add_sales(_sale)
            flash("Sales Record Created.!!!", 'Success')
            return redirect(url_for('salesform'))
        else:
            flash("Could not find product in Inventory Check Warehouse Number Or Quantity.!!!", 'ERROR')

    return render_template('salesform.html', form = form)

@app.route('/purchases', methods = ['POST', 'GET'])
def purchases():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = searchform()
    form.c_comp.label = 'Company'
    form.name.label = "Name"
    page = request.args.get(get_page_parameter(), type=int, default=1)
    skip = ((page-1)*10)
    users = db.purchase.find().sort([('Date',pymongo.DESCENDING)]).skip(skip).limit(10)
    pagination = Pagination(page=page, total=users.count(), search=False, record_name='Expenses', css_framework='bootstrap4')

    if request.method == 'POST':
        name = re.compile(r''+request.form['name1'], re.I)
        phone = re.compile(r''+request.form['phone'], re.I)
        fromdate = request.form['from']
        todate = request.form['to']
        if fromdate!='' and todate!='':
            q = {'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}, 
            'Date': {'$gte': datetime.strptime(fromdate, '%m/%d/%Y'), '$lte': (datetime.strptime(todate, '%m/%d/%Y')) }
                }
                    
        else:
            q = {'Name': {'$regex': name}, 
            'Phone': {'$regex': phone}}


        return render_template('purchase.html', arr=get_purchase(q), form=form, redirect = redirect)
    return render_template('purchase.html', arr=users, form=form, redirect = redirect, pagination=pagination)
    
@app.route("/variety/<product>")
def product(product):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    arr = [("", "Choose")]
    for i in get_variety(product):
        obj = {}
        obj["value"] =  i 
        obj["name"]  =  i 
        arr.append(obj)
    return jsonify({'variety': arr})

@app.route("/Brand/<product>/<variety>")
def Brand(product, variety):    
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    arr = [('choose', 'Choose')]
    for i in get_comp(product, variety):
        obj = {}   
        obj["value"] =  i 
        obj["name"]  =  i 
        arr.append(obj)
    return jsonify({'Brand': arr})

@app.route("/expiry/<product>/<variety>/<Brand>")
def expiry(product, variety, Brand):    
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    arr = [('choose', 'Choose')]
    for i in get_expiry(product, variety, Brand):
        obj = {}   
        obj["value"] =  i 
        obj["name"]  =  i 
        arr.append(obj)
    return jsonify({'expiry': arr})

@app.route("/reports")
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    querry = {'$lte': datetime.today(), '$gte': datetime.today()-timedelta(1)}
    purchase_records, purchase_amount = (getTodaysPurchaserRecords(querry))
    purchase_amount = 'Rs. ' + str((format (purchase_amount, ',d'))) + '/-'
    sale_records, sale_amount = getTodaysSaleRecords(querry)
    
    sale_amount = 'Rs. ' + str((format (sale_amount, ',d'))) + '/-'

    var1, var2 = "Today's Total Purchase:", "Today's Total Sale:"

    arr1 = ['Productname',	'Variety',	"Brand",	'Amount',	'Quantity',	'Seller']
    arr2 = ['Productname',	'Variety',	"Brand",	'Amount',	'Quantity',	'Buyer']
    

    return render_template('reports.html', purchase_amount=purchase_amount, 
                                        purchase_records=purchase_records, 
                                        sale_amount = sale_amount, 
                                        sale_records = sale_records,
                                        arr1 = arr1, arr2 = arr2,
                                        format = format)

@app.route("/restock")
def restock():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    querry = {'$lte': datetime.today()+timedelta(150)}
    inventoryfun = inventoryfunc()
    nearexpiry, expireamount = inventoryfun.find({"expiry":querry}), inventoryfun.count_documents({"expiry":querry})    
    # sale_amount = 'Rs. ' + str((format (sale_amount, ',d'))) + '/-'
    var2, var1 = "Out of Stock:", "About to Expire:"

    arr1 = ['Productname',	'Variety',	"Brand",	'Quantity',	'expiry']
    arr2 = ['Productname',	'Variety',	"Brand",	'Quantity',	'expiry']

    return render_template('reports.html', purchase_amount=expireamount, 
                                        purchase_records= nearexpiry, 
                                        sale_amount=getOutOfStock(1000).count(), 
                                        sale_records = getOutOfStock(1000),
                                        var1 = var1, var2 = var2,
                                        arr1 = arr1, arr2 = arr2,
                                        format = format)

@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        session['notadmin'] = False
        if not session.get('notadmin'):
            return "Not logged in"
    else:
        session['logged_in'] = False
        session['notadmin'] = False
        for key in session.keys():
            session.pop(key)
    return render_template('logout.html')

@app.route("/changeStatusToPaid/<account>/<ID>/<amount>/<desc>", methods = ['GET'])
def changeStatusToPaid(ID, account, amount, desc):
    amount =int(amount)
    if account == 'Pay':
        cursor = db.purchase.find_one({'_id': ObjectId(ID)} )
        amount_paid = 0
        amount_remaining = 0
        description = []
        for i in cursor:
            amount_paid = cursor['amount_paid']
            amount_remaining = cursor['amount_remaining']
            description = cursor['Description']
        amount_paid+=amount
        amount_remaining-=amount
        paydate = "Last Payment: Rs."+ str(amount)+ " at " + str(datetime.today().strftime('%d-%b-%Y')) + ": " + desc
        description.append(paydate)
        if amount_remaining == 0:
            db.purchase.update_one({'_id': ObjectId(ID)}, { "$set" :{'amount_paid': amount_paid, 'amount_remaining': amount_remaining, 'Description': description, 'transaction': 'Cash'}})
        elif amount_remaining > 0:
            db.purchase.update_one({'_id': ObjectId(ID)}, { "$set" :{'amount_paid': amount_paid, 'amount_remaining': amount_remaining, 'Description': description }})
        else:
            return "Error in Transaction"

        
    if account == 'Recieve':
        cursor = db.sales.find_one({'_id': ObjectId(ID)} )
        amount_paid = 0
        amount_remaining = 0
        description = []
        for i in cursor:
            amount_paid = cursor['amount_paid']
            amount_remaining = cursor['amount_remaining']
            description = cursor['Description']

        amount_paid+=amount
        amount_remaining-=amount        
        paydate = "Last Payment: " + str(amount)+ " At " +str(datetime.today().strftime('%d-%b-%Y')) + ": " + desc
        description.append(paydate)

        if amount_remaining == 0:
            db.sales.update_one({'_id': ObjectId(ID)}, { "$set" :{'amount_paid': amount_paid, 'amount_remaining': amount_remaining, 'Description': description, 'transaction': 'Cash'}})
        elif amount_remaining > 0:
            db.sales.update_one({'_id': ObjectId(ID)}, { "$set" :{'amount_paid': amount_paid, 'amount_remaining': amount_remaining, 'Description': description }})
        else:
            return "Error in Transaction"


    return "Transaction Completed"

@app.route("/printtoPDF/<ID>/<action>", methods = ['GET'])
def printtoPDF(ID, action):
    import pdfkit
    if action == 'Recieve':
        cursor = db.sales.find({'_id' : ObjectId(ID) })
        arr= []
        for i in cursor:
            arr.append(i)
        pdfkit.from_string(arr, 'out.pdf')
        return ''

@app.route("/transaction/<ID>/<account>", methods = ['GET', 'POST'])
def transaction(ID, account):
    arr = ['Name', 'country', 'Phone', 'Company', 'Quantity', 
    'Total', 'PriceperKG', 'expiry', 
    'manufacture', 'transaction', 'Date', 
    'amount_remaining', 'amount_paid']

    arr2 = ['Name', 'country', 'Phone', 'Company', 'Quantity', 
    'Total', 'transaction', 'Date', 
    'amount_remaining', 'amount_paid']
    
    if account == 'Recieve':
        var = 'Sales'
        cursor = db.sales.find_one({'_id': ObjectId(ID)} )
        desc = []
        for i in cursor:
            desc = cursor['Description']

        return render_template('transaction.html', arr = cursor, arr2 = arr2, desc = desc, var =var )
    if account == 'Pay':
        var = 'Purchase'
        cursor = db.purchase.find_one({'_id': ObjectId(ID)} )
        desc = []
        for i in cursor:
            desc = cursor['Description']
        
        return render_template('transaction.html', arr = cursor, arr2 = arr, desc = desc, var =var)



if __name__ == "__main__":
    app.run(debug=True)
