from datetime import datetime,timedelta 

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from dbcon import (
    add_purchase, add_sales, addinform, addQuantity, get_comp, get_data,
    get_sales, get_variety, getTodaysPurchaserRecords, getTodaysSaleRecords,
    sform, addnewform, update_inventory, add_item, getOutOfStock, searchform,
    get_purchase, get_productname, db, getQuantityFromWh, getSalesOf6Months)

app = Flask(__name__)
app.secret_key = 'loginner'

users = {'admin' : 'pass!@#$admin',
        'vimal'   : 'hemnani!@#',}

# @app.route('/')
# def main():
#     return render_template(url_for('loginform'))

@app.route("/account" , methods=['Post','GET'])
def account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = searchform()
    form.transaction.choices = [('Payable','Payable'), ('Recievable','Recievable')]
    form.transaction.label = "Select Accounts"

    column = ['Name Name',	
    "Product Name",	
    "Name's City",
    "Quantity",	
    "Variety",	
    "Company name",	
    "Total Price",	
    "Date",	
    "Transaction"]

    if request.method == 'POST':
        if form.transaction.data == "Recievable":
            _sale = {"Name":form.name.data,
                    "Productname":form.product.data,
                    "City": form.city.data,
                    "Brand":form.Brand.data,
                    "Variety": form.variety.data,
                    "Company": form.c_comp.data,
                    "transaction" : form.transaction.data}
            querry = {"transaction" : "Credit"}
            for i in (_sale):
                if len(_sale[i])>0:
                    querry[i] = _sale[i]

            return render_template('account.html', arr=db.sales.find({"transaction" : "Credit"}), form=form, 
            heading = 'Accounts '+   (form.transaction.data), redirect = redirect)
        if form.transaction.data == "Payable":
            _sale = {"Name":form.name.data,
                    "Productname":form.product.data,
                    "City": form.city.data,
                    "Brand":form.Brand.data,
                    "Variety": form.variety.data,
                    "Company": form.c_comp.data,
                    "transaction" : form.transaction.data}
            querry = {"transaction" : "Credit"}
            for i in (_sale):
                if len(_sale[i])>0:
                    querry[i] = _sale[i]

            return render_template('account.html', arr=db.purchase.find({"transaction" : "Credit"}), 
            form=form, heading = 'Accounts '+(form.transaction.data), redirect = redirect)

    return render_template('account.html', arr=db.sales.find({"transaction" : "Credit"}),
     form=form, heading = 'Accounts '+'Recievable', redirect = redirect)

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

    return render_template('index.html')

@app.route("/home")
def home():

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    values = getQuantityFromWh()
    labels = ['Warehouse 1', 'Warehouse 2', 'Warehouse 3']
    colors = ["#F7464A", "#46BFBD", "#FDB45C"]
    
    (bar_labels, bar_values) = getSalesOf6Months()
    max2 = max(bar_values)
    outofstock = getOutOfStock(100)

    return render_template('home.html', max=17000, 
    set = zip(values, labels, colors ), 
    max2 = max2, labels=bar_labels, values=bar_values,
    outofstock=outofstock)

@app.route("/inventory")
def inventory():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    arr = get_data()
    return render_template('inventory.html', arr=arr, redirect = redirect)

@app.route("/sales"  , methods=['Post','GET'])
def sales():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = searchform()

    if request.method == 'POST':
        _sale = {"Name":form.name.data,
                "Productname":form.product.data,
                "City": form.city.data,
                "Brand":form.Brand.data,
                "Variety": form.variety.data,
                "Company": form.c_comp.data,
                "transaction" : form.transaction.data}
        querry = {}
        for i in (_sale):
            if len(_sale[i])>0:
                querry[i] = _sale[i]

        return render_template('sales.html', arr=get_sales(querry), form=form, redirect = redirect)
    return render_template('sales.html', arr=get_sales(), form=form, redirect = redirect)

@app.route("/addinventory" , methods=['Post','GET'])
def addinventory():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    form = addinform()
    form.product.choices = get_productname()
    form_addnew =  addnewform()   
    # if form.submit.data and form.validate_on_submit:
    if request.form.get('Submit') == 'Submit': 
        purchase = {
                "Productname":form.product.data,
                "Variety": form.variety.data,
                "Brand":form.Brand.data,
                "Name": form.name.data,
                "City": form.city.data,
                "Company": form.c_comp.data,
                "Quantity": form.quan.data,
                "Total": form.price.data,
                "transaction" : form.transaction.data,
                "Date": datetime.now() 
                }
       


        if addQuantity(form.product.data,form.variety.data,form.Brand.data, form.quan.data, form.warehouse.data):
            add_purchase(purchase)
            flash("Purchase Record Created.!!!", 'Success') 
            # form = addinform()
            return redirect(url_for('addinventory'))
        else:
            flash("Could not find product in Inventory.!!!", 'ERROR')

    if request.form.get('Submit') == 'Add Item':
        purchase = {"Productname":form_addnew.product.data,
                   "Variety": form_addnew.variety.data,
                   "Brand":form_addnew.Brand.data,
                    "Name": form_addnew.name.data,
                    "City": form_addnew.city.data,
                    "Company": form_addnew.c_comp.data,
                    "Quantity": form_addnew.quan.data,
                    "Total": form_addnew.price.data,
                    "transaction" : form_addnew.transaction.data,
                    "Date": datetime.now() }

        dicts = {"Productname" : form_addnew.product.data, 
                 "Variety"     : form_addnew.variety.data, 
                 "Brand"       : form_addnew.Brand.data, 
                 "Quantity"    : form_addnew.quan.data,
                 "Purchase_price": form_addnew.price.data,
                 "Warehouse" : form_addnew.warehouse.data,
                 "Date" : datetime.now()
                 }



        if add_item(dicts) and add_purchase(purchase):
            flash("Purchase Record Created and added item in inventory.!!!", 'Success')
            return redirect(url_for('addinventory'))
        else:
            flash("There was an Error.!!!", 'ERROR')

    return render_template('addinventory.html', form = form, form_addnew = form_addnew)

@app.route("/salesform" , methods=['Post','GET'])
def salesform():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    form = sform()
    form.product.choices = get_productname()    
    if request.method == 'POST':
        _sale = {"Name":form.name.data,
                "Productname":form.product.data,
                "City": form.city.data,
                "Quantity": form.quan.data,
                "Brand":form.Brand.data,
                "Variety": form.variety.data,
                "Company": form.c_comp.data,
                "Total" : form.price.data,
                "Warehouse" : form.warehouse.data,
                "transaction" : form.transaction.data,
                "Date": datetime.now() }        
        if update_inventory(form.product.data,form.variety.data,form.Brand.data, form.quan.data, form.warehouse.data):
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

    if request.method == 'POST':
        _sale = {"Name":form.name.data,
                "Productname":form.product.data,
                "City": form.city.data,
                "Brand":form.Brand.data,
                "Variety": form.variety.data,
                "Company": form.c_comp.data,
                "transaction" : form.transaction.data}
        querry = {}
        for i in (_sale):
            if len(_sale[i])>0:
                querry[i] = _sale[i]

        return render_template('purchase.html', arr=get_purchase(querry), form=form, redirect = redirect)
    return render_template('purchase.html', arr=get_purchase(), form=form, redirect = redirect)
    
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

@app.route("/reports")
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    querry = {'$lte': datetime.today(), '$gte': datetime.today()-timedelta(1)}
    purchase_records, purchase_amount = (getTodaysPurchaserRecords(querry))
    purchase_amount = 'Rs. ' + str((format (purchase_amount, ',d'))) + '/-'
    sale_records, sale_amount = getTodaysSaleRecords(querry)
    
    sale_amount = 'Rs. ' + str((format (sale_amount, ',d'))) + '/-'

    return render_template('reports.html', purchase_amount=purchase_amount, 
                                        purchase_records=purchase_records, 
                                        sale_amount=sale_amount, 
                                        sale_records = sale_records,
                                        format = format)

@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        return "Not logged in"
    else:
        session['logged_in'] = False
    return render_template('logout.html')

if __name__ == "__main__":
    app.run(debug=True)
