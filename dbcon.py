from datetime import date, datetime,timedelta

import pymongo
from flask_wtf import FlaskForm
from wtforms import (IntegerField, RadioField, SelectField, SubmitField,
                     TextAreaField, TextField, ValidationError, validators, DateField)




today = date.today().strftime("%d/%m/%Y")
sample = {"Productname":"Productname",
"Quantity": 123,
"Variety": "variety",
"Brand": "Brand",
"Purchase_Price" : 2.1,
"Date": today
}

myclient = pymongo.MongoClient("mongodb+srv://mujtaba:developer@hsc-vp2me.mongodb.net/test?retryWrites=true&w=majority")


mydb = myclient["HSC"]
inventory = mydb["inventory"]
sales = mydb["sales_records"]
purchase = mydb["purchase_records"]

class db():
    inventory = mydb["inventory"]
    sales = mydb["sales_records"]
    purchase = mydb["purchase_records"]
    sauda = mydb["sauda"]
    expense = mydb['expense']



def update_inventory(product, variety, brand, quantity, warehouse): #Subtracting Quantity in existing item (When there is a Sale) 
    arr = inventory.find({"Productname":product,"Variety": variety,"Brand":brand, "Warehouse": int(warehouse)} )
    new_quantity = arr[0]['Quantity'] - quantity
    if new_quantity < 0:
        return False
    result = inventory.update_one({"Productname":product,"Variety": variety,"Brand":brand} ,{ '$set' : {'Quantity': (new_quantity) } })
    return True

def add_sales(dicts):#Add a document in sale Records
    sales.insert(dicts)

def add_item(dicts):#Add a document in Inventory
    try:
        inventory.insert(dicts)
        return True
    except:
        return False

def add_purchase(dicts):#Add a document in purchase record and returns Boolean
    try:
        purchase.insert(dicts)
        return True
    except:
        return False

def get_data():#Returns all the inventory Records from Database
    return inventory.find({})

def get_sales(querry = {}): #Returns all the sale Records from Database
    return sales.find(querry).sort([('Date',pymongo.DESCENDING)])

def get_purchase(querry = {}): #Returns all the sale Records from Database
    return purchase.find(querry).sort([('Date',pymongo.DESCENDING)])

def get_variety(prod):#Shortlisting varieties from crops, used for dropdown menus
    arr = inventory.distinct('Variety',{"Productname": prod})
    return arr

def get_comp(prod, var): #Shortlisting Brand names from crops and varieties, used for dropdown menus
    arr =inventory.distinct("Brand",{"Productname": prod, "Variety":var})
    return arr

def get_productname():#Getting all the product names in the inventory
    arr = [('',"Choose")]
    for i in inventory.distinct('Productname'):
        tup = ( i , i )
        arr.append(tup)
    return arr

def addQuantity(prd, var, comp, q , w): #adding Quantity in existing item 
    try:
        arr = inventory.find({"Productname":prd,"Variety": var,"Brand":comp, "Warehouse": w} )
        new_quantity = arr[0]['Quantity'] + q
        if new_quantity < 0:
            return (arr[0]['Quantity'])
        result = inventory.update_one({"Productname":prd,"Variety": var,"Brand":comp} ,{ '$set' : {'Quantity': (new_quantity) } })
        return result.matched_count > 0 
    except:
        return False

def getTodaysPurchaserRecords(querry): #Returns total amount of purchase and total records of purchase of present day
    arr = []
    amount = 0
    for i in purchase.find({"Date":querry}):
        amount +=(i['Total'])
        arr.append({'Productname':i['Productname'],
                    'Variety':i['Variety'],
                    'Brand':i['Brand'],
                    "total Amount":i["Total"],
                    'Quantity':i['Quantity'],
                    "Company":i["Company"]}
                    )
    return (arr, amount)

def getTodaysSaleRecords(querry): #Returns total amount of sale and total records of sale of present day
    arr = []
    amount = 0
    for i in sales.find({"Date":querry}):
        amount +=(i['Total'])
        print(i['Date'])
        arr.append({'Productname':i['Productname'],
                    'Variety':i['Variety'],
                    'Brand':i['Brand'],
                    "total":i["Total"],
                    'Quantity':i['Quantity'],
                    "Company":i["Company"]})
        
    return (arr, amount)

def getOutOfStock(qt):
    querry = {'$lte':qt}
    return inventory.find({"Quantity": querry})

class sform(FlaskForm): #Sales form class
    
    product = SelectField('Select Crop',[validators.DataRequired("Please Select Crop.")] ,choices = [])
    variety = SelectField('Select Variety',[validators.DataRequired("Please Select Variety.")], choices = [])
    Brand = SelectField('Select Brand',[validators.DataRequired("Please Select Brand.")], choices = [])     
     
    name = TextField("Customer Name ",[validators.DataRequired("Please enter Name.")])
    country = TextField("Customer country ",[validators.DataRequired("Please enter country.")])  
    c_comp = TextField("Company",[validators.DataRequired("Please enter customer's Brand name.")])  
    price  = IntegerField("Selling Price (KG)",[validators.DataRequired("Please enter selling price.")])

    description = TextField("Description",[validators.DataRequired("Please enter Description.")])


    phone = IntegerField("Phone",[validators.DataRequired("Please enter Phone Number.")])

    quan = IntegerField("Quantity",[validators.DataRequired("Please enter Quantity in Kilograms.")])  
    warehouse = IntegerField("Warehouse #",[validators.DataRequired("Please enter Warehouse #.")])

    transaction = SelectField('Select Cash/Credit',[validators.DataRequired("Please Select Cash/Credit.")], choices = [('Cash','Cash'),('Credit','Credit')])
  
    submit = SubmitField("Submit")  

class addinform(FlaskForm): #Form class for adding Quantity in existing item
    product = SelectField('Select Crop',[validators.DataRequired("Please Select Crop.")] ,choices = get_productname())
    variety = SelectField('Select Variety',[validators.DataRequired("Please Select Variety.")], choices = [])
    Brand = SelectField('Select Brand',[validators.DataRequired("Please Select Brand.")], choices = [])     
    price  = IntegerField("Purchase price per KG",[validators.DataRequired("Please enter price.")])
    quan = IntegerField("Quantity",[validators.DataRequired("Please enter Quantity in Kilograms.")])  

    name = TextField("Name ",[validators.DataRequired("Please enter Name.")])
    country = TextField("country ",[validators.DataRequired("Please enter country.")])  
    c_comp = TextField("Company",[validators.DataRequired("Please enter customer's Brand name.")])  


    expiry = DateField('Expiry Date', format='%m/%d/%Y')
    manufacture = DateField('Manufacture Date', format='%m/%d/%Y')


    warehouse = IntegerField("Warehouse #",[validators.DataRequired("Please enter Warehouse.")])  
       
    transaction = SelectField('Select Cash/Credit',[validators.DataRequired("Please Select Cash/Credit.")], choices = [('Cash','Cash'),('Credit','Credit')])

    phone = IntegerField("Phone",[validators.DataRequired("Please enter Phone Number.")])


    submit = SubmitField("Submit")  

class addnewform(FlaskForm): #Form class for adding a new item in inventory

    product = TextField('Crop Name',[validators.DataRequired("Please insert Crop.")])
    variety = TextField('Variety',[validators.DataRequired("Please insert Variety.")])
    Brand = TextField('Brand',[validators.DataRequired("Please insert Brand.")])     
    price  = IntegerField("Purchase price per KG",[validators.DataRequired("Please enter price.")])
    quan = IntegerField("Quantity",[validators.DataRequired("Please enter Quantity.")])
    warehouse = IntegerField("Warehouse #",[validators.DataRequired("Please enter Warehouse.")])  
 
    expiry = DateField('Expiry Date', format='%m/%d/%Y')
    manufacture = DateField('Manufacture Date', format='%m/%d/%Y')

    name = TextField("Name ",[validators.DataRequired("Please enter Name.")])
    country = TextField("country ",[validators.DataRequired("Please enter country.")])  
    c_comp = TextField("Company",[validators.DataRequired("Please enter customer's Brand name.")])  

    transaction = SelectField('Select Cash/Credit',[validators.DataRequired("Please Select Cash/Credit.")], choices = [('Cash','Cash'),('Credit','Credit')])
    phone = IntegerField("Phone",[validators.DataRequired("Please enter Phone Number.")])

    submit2 = SubmitField("Submit")

class searchform(FlaskForm): #Form class for adding a new item in inventory
    product = TextField('Crop Name')
    variety = TextField('Variety')
    Brand = TextField('Brand')      
    name = TextField("Buyer's Name ")
    country = TextField("country")  
    c_comp = TextField("Company")  

    transaction = SelectField('Select Cash/Credit', choices = [('','Both'),('Cash','Cash'),('Credit','Credit')])

    submit2 = SubmitField("Submit")


def getQuantityFromWh():
    arr = []
    s = inventory.find({"Warehouse": 1})
    c=0
    for i in s:
        c+=i['Quantity']
    arr.append(c)

    s = inventory.find({"Warehouse": 2})
    c=0
    for i in s:
        c+=i['Quantity']
    arr.append(c)

    s = inventory.find({"Warehouse": 3})
    c=0
    for i in s:
        c+=i['Quantity']
    arr.append(c)
    return arr


def foo():
    def getLast6Month(days):
        return(datetime.now() - timedelta(days=days))
    
    days = 0

    for i in range(6):
        days += 30
        yield(getLast6Month(days))

def getSalesOf6Months():
    arr = []  
    tot = []
    for i in foo():
        querry = {'$lt':i+timedelta(30), '$gt': i}
        cursor = sales.find({"Date":querry })
        total = 0
        for i in cursor:
            total+=i['Total']
        arr.append(querry['$gt'].strftime('%b-%y') + ' Sales :' )
        tot.append(total)
    return (arr, tot)

def sauda_():
    return mydb["sauda"]
