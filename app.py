from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/campers", methods=['GET','POST'])
def campers():
    if request.method == "GET":
        return render_template("datepickercamper.html", currentdate = datetime.now().date())
    else:
        campDate = request.form.get('campdate')
        connection = getCursor()
        connection.execute("SELECT * FROM bookings join sites on site = site_id inner join customers on customer = customer_id where booking_date= %s;",(campDate,))
        print(campDate)
        camperList = connection.fetchall()
        
        print(camperList)
        return render_template("datepickercamper.html", camperlist = camperList)
        #return render_template("camperlist.html", camperlist = camperList)
# @app.route("/campers")
# def campers():
#     connection = getCursor()
#     connection.execute("SELECT * FROM bookings join sites on site = site_id inner join customers on customer = customer_id where booking_date= %s;",('2024-06-01',))
#     camperList = connection.fetchall()
#     print(camperList)
#     return render_template("datepickercamper.html", camperlist = camperList)

@app.route("/booking", methods=['GET','POST'])
def booking():
    if request.method == "GET":
        return render_template("datepicker.html", currentdate = datetime.now().date())
    else:
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')
        firstNight = date.fromisoformat(bookingDate)
        # print(occupancy)
        lastNight = firstNight + timedelta(days=int(bookingNights))
        connection = getCursor()
        connection.execute("SELECT * FROM customers;")
        customerList = connection.fetchall()
        connection.execute("select * from sites where occupancy >= %s AND site_id not in (select site from bookings where booking_date between %s AND %s);",(occupancy,firstNight,lastNight))
        siteList = connection.fetchall()
       
        print(request.form)       
        return render_template("bookingform.html",customerlist = customerList, bookingdate=bookingDate, sitelist = siteList, bookingnights = bookingNights,occupancy= occupancy)    

@app.route("/booking/add", methods=['POST'])
def makebooking():
    print(request.args)
    print(request.form)
    customer= request.form.get('customer')
    site = request.form.get('site')
    bookingDate = request.form.get('bookingdate')
    bookingNights = request.form.get('bookingnights')
    occupancy = request.form.get('occupancy')
    # bookingid = bookingIdList
    connection = getCursor()
    # connection.execute("SELECT max(booking_id) FROM scg.bookings;")
    # bookingId = connection.fetchall()
    print(customer)
    print(site)
    print(bookingDate)
    print(bookingNights)
    print(occupancy)
    # newBookingId = bookingId[0][0]+1
    # print(newBookingId)

    connection.execute("INSERT INTO bookings (site, customer, booking_date, occupancy) VALUES(%s,%s,%s,%s);",(site, customer, str(bookingDate), occupancy,))
    return redirect("/campers")

# @app.route("/customer", methods=['GET','POST'])
# def customer():
#      if request.method == "GET":
#         return redirect("/customer/search")
#      else:
#         customerId = request.form.get('customerid')
#         connection = getCursor()
#         connection.execute("SELECT * FROM customers WHERE customer_id = %s;", (int(customerId),))
#         customerData = connection.fetchall()
#         print(request.form)
#         return render_template("customerdetails.html",customerdata =customerData)
        

@app.route("/customer/search", methods=['GET','POST'])
def customer():
     if request.method == "GET":
        return render_template("customersearch.html")
     else:
        customerId = request.form.get('customerid')
        connection = getCursor()
        connection.execute("SELECT * FROM customers WHERE customer_id = %s;", (int(customerId),))
        customerData = connection.fetchall()
        print(request.form)
        return render_template("customerdetails.html",customerdata =customerData)

@app.route("/customer/add", methods=['POST'])
def addcustomer():
       
            firstName = request.form.get('firstname')
            familyName = request.form.get('familyname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            connection = getCursor()
            connection.execute("INSERT INTO customers (firstname, familyname, email, phone) VALUES(%s,%s,%s,%s);",(firstName, familyName, email, phone,))
            
            return render_template("customeradd.html")

# @app.route("/customer/edit", methods=['GET','POST'])
# def editcustomer():
#         if request.method == "GET" :
            
#             customerId = request.form.get('customerid')
#             connection = getCursor()
#             connection.execute("SELECT * FROM customers WHERE customer_id = %s;", (int(customerId),))
#             customerData = connection.fetchall()
#             print(request.form)
#             return redirect("customersearch.html",customerdata=customerData)
#         else:
#             print(request.form)
#             #customerId =request.form.get('customerid')
#             firstName = request.form.get('firstname')
#             familyName = request.form.get('familyname')
#             email = request.form.get('email')
#             phone = request.form.get('phone')
#             connection = getCursor()
#             #print(customerId)
#             connection.execute("UPDATE customers SET firstname = %s, familyname = %s, email = %s, phone = %s WHERE customer_id = %s;"
# ,(firstName, familyName, email, phone,customerId))
#             return render_template("customeredit.html")


@app.route("/mycustomer", methods=['GET','POST'])
def mycustomer():
    if request.method == "GET":
        return render_template("mycustomer.html")
    else:
        print(request.args)
        print(request.form)
        customerId = request.form.get('customerid')       
        return render_template("mycustomeredit.html",customerid =customerId)    

@app.route("/mycustomer/edit", methods=['POST'])
def mycustomeredit():
    print(request.args)
    print(request.form)
    customerId = request.form.get('customerid')
    firstName = request.form.get('firstname')
    familyName = request.form.get('familyname')
    email = request.form.get('email')
    phone = request.form.get('phone')       
    connection = getCursor()
    # connection.execute("SELECT max(booking_id) FROM scg.bookings;")
    # bookingId = connection.fetchall()
    print(request.form['customerid'])
    print(firstName)
    print(familyName)
    print(email)
    print(phone)
    # newBookingId = bookingId[0][0]+1
    # print(newBookingId)

    connection.execute("UPDATE customers SET firstname = %s, familyname = %s, email = %s, phone = %s WHERE customer_id = %s;"
,(firstName, familyName, email, phone,customerId,))
    return redirect('/customer/search')