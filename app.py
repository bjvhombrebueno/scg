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
    connection.execute("SELECT max(booking_id) FROM scg.bookings;")
    bookingId = connection.fetchall()
    print(customer)
    print(site)
    print(bookingDate)
    print(bookingNights)
    print(occupancy)
    newBookingId = bookingId[0][0]+1
    print(newBookingId)

    connection.execute("INSERT INTO bookings (booking_id, site, customer, booking_date, occupancy) VALUES(%s,%s,%s,%s,%s);",(str(newBookingId), site, customer, str(bookingDate), occupancy,))
    return redirect("/campers")

@app.route("/customer", methods=['GET','POST'])
def customer():
     if request.method == "GET":
        return render_template("customersearch.html")
     else:
        customerId = request.form.get('customerid')
        print(request.form)
        print(type(customerId))
        connection = getCursor()
        # connection.execute("SELECT * FROM customers WHERE customer_id = 1661;")
        connection.execute("SELECT * FROM customers WHERE customer_id = %s;", (int(customerId),))
        customerData = connection.fetchall()

        return render_template("customersearch.html",customerdata =customerData)