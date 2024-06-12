from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
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


def is_valid_firstname(firstname):
    # Check if firstname matches the format
    if not re.search(r"(^[a-zA-Z][a-zA-Z\s]{0,60}[a-zA-Z]$)", firstname):
        return False
    return True

def is_valid_familyname(familyname):
    # Check if familyname matches the format
    if not re.search(r"(^[a-zA-Z][a-zA-Z\s]{0,60}[a-zA-Z]$)", familyname):
        return False
    return True

def is_valid_email(email):
    # Check if email matches the format
    if not re.match(r"^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$", email):
        return False
    return True

def is_valid_phone(phone):
    # Check if phone matches the format
    if not re.match(r"^0\d{8,10}$", phone):
        return False
    return True


@app.route("/")
def home():
    #Displays the homepage for the app
    return render_template("home.html")

@app.route("/campers", methods=['GET','POST'])
def campers():
    # There are 2 ways to get to campers page, when it is first entered by 'GET' the user will be asked for the date, 
    # when entered by 'POST' it will list the campers for that date. 
    
    if request.method == "GET":
        return render_template("datepickercamper.html", currentdate = datetime.now().date())
    else:
        campDate = request.form.get('campdate')
        connection = getCursor()
        #SQL to get all the campers for the date
        connection.execute("SELECT * FROM bookings join sites on site = site_id inner join customers on customer = customer_id where booking_date= %s ORDER BY familyname;",(campDate,))
        print(campDate)
        camperList = connection.fetchall()
        
        print(camperList)
        return render_template("datepickercamper.html", camperlist = camperList, campdate=campDate)


@app.route("/booking", methods=['GET','POST'])
@app.route("/bookingget/?customerid=<customerid>", methods=['GET','POST'])
def booking(customerid=None):
    # There are 2 ways to get to the booking page, when it is first entered by 'GET' the user will be asked for the date, 
    # occupancy and the number of nights,and when entered by 'POST'it will list the available sites and choose which customer to make the booking for. 
    # Once those are submitted and validated, then it will proceed to the confirmation page. 

    if request.method == "GET":
        return render_template("datepicker.html", currentdate = datetime.now().date(),customerid=customerid)
    else:
        customerid=customerid
        bookingNights = request.form.get('bookingnights')
        bookingDate = request.form.get('bookingdate')
        occupancy = request.form.get('occupancy')
        firstNight = date.fromisoformat(bookingDate)
        
        lastNight = firstNight + timedelta(days=int(bookingNights))
        connection = getCursor()
        connection.execute("SELECT * FROM customers ORDER BY familyname;")
        customerList = connection.fetchall()
        #SQL to select all the available sites for booking
        connection.execute("select * from sites where occupancy >= %s AND site_id not in (select site from bookings where booking_date between %s AND %s);",(occupancy,firstNight,lastNight))
        siteList = connection.fetchall()
       
        print(request.form)       
        return render_template("bookingform.html",customerlist = customerList, bookingdate=bookingDate, sitelist = siteList, bookingnights = bookingNights,occupancy= occupancy,customerid=customerid)    

@app.route("/bookingget/", methods=['GET','POST'] )
def bookingdetailsget():
    # This is just to get the correct argument to be passed to the customerhome 
    return booking(request.args['customerid'])

@app.route("/booking/add", methods=['POST'])
def makebooking():
    #This part gets the inputs from the form
    customer= request.form.get('customer')
    site = request.form.get('site')
    bookingDate = date.fromisoformat(request.form.get('bookingdate'))
    bookingNights = request.form.get('bookingnights')
    occupancy = request.form.get('occupancy')
    connection = getCursor()
    connection.execute("SELECT * FROM customers WHERE customer_id = %s;", (int(customer),))
    customerData = connection.fetchone()
    for i in range(0,int(bookingNights)):
        #Loop and SQL to insert the booking into the database one night at a time
        connection.execute("INSERT INTO bookings (site, customer, booking_date, occupancy) VALUES(%s,%s,%s,%s);",(site, customer, str(bookingDate), occupancy,))
        bookingDate = bookingDate +timedelta(days=1)
    bookingDate = bookingDate -timedelta(days=int(bookingNights)) # this is for the confirmation display only
    
    return render_template("/bookingconfirmation.html",customerdata=customerData, site = site, bookingdate = bookingDate, bookingnights = bookingNights, occupancy=occupancy )
     

@app.route("/customer/search", methods=['GET','POST'])
def customersearch():
    #  There are 2 ways to get into the customer search page, when 'GET' is used it displays the input box for the search string 
    # and by ('POST') it displays all the search results. 

     if request.method == "GET":
        return render_template("customersearch.html")
     else:
        customerName = request.form.get('customername')
        #SQL to return all of the matches of the search string
        sql= "SELECT * FROM customers WHERE firstname LIKE '%"+ customerName + "%' OR familyname LIKE '%"+ customerName + "%' ORDER BY familyname;"
        print(sql)
        connection = getCursor()
        connection.execute(sql)
        customerData = connection.fetchall()
        print(request.form)
        print(customerData)
        return render_template("customersearch.html",customerdata =customerData)

@app.route("/customer/add", methods=['GET','POST'])
def customeradd():
     # For this part the input values from the form are checked if they are valid
    if request.method == "GET":
        return render_template("enterdetails.html")
    else:
            
        firstName = request.form.get('firstname')
        familyName = request.form.get('familyname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        # Flags are added to send the result of the validation to the confirmation page
        flagFirstName = is_valid_firstname(firstName)
        flagFamilyName = is_valid_familyname(familyName)
        flagEmail = is_valid_email(email)
        flagPhone = is_valid_phone(phone)
        # If they are all of them are valid they are written to the database, otherwise nothing is done.
        if (is_valid_firstname(firstName) and is_valid_familyname(familyName) and is_valid_email(email) and is_valid_phone(phone)):
            connection = getCursor()
            connection.execute("INSERT INTO customers (firstname, familyname, email, phone) VALUES(%s,%s,%s,%s);",(firstName, familyName, email, phone,))
        else:
            pass
        #Show the confirmation result
        return render_template("enterdetailsconfirmation.html", firstname = firstName, familyname=familyName, email = email, phone = phone,flagfirstname = flagFirstName, flagfamilyname = flagFamilyName, flagemail= flagEmail, flagphone =flagPhone)         

@app.route("/customerhome", methods=['GET','POST'])
@app.route("/customerhomeget/?customerid=<customerid>", methods=['GET','POST'])
def customerhome(customerid=None):
    # There are 2 ways to get into the customer home page, when 'GET' is used it displays the selection box for the customer 
    # and 2 buttons ('POST') for either editing or generating the report for the selected customer.  
    # Editing and viewing are grouped together as they both need a customer id to function.
     
    if request.method == "GET":
        connection = getCursor()
        connection.execute("SELECT * FROM customers ORDER BY familyname;")
        # customerData = connection.fetchall()
        customerList = connection.fetchall()
        # return render_template("customerhome.html",customerdata = customerData, customerid=customerid)
        return render_template("customerhome.html",customerlist = customerList, customerid=customerid)
    else:
        customerId = request.form.get('customerid')
        # When the Edit button is pressed, there is redirection to the enterdetails page which it shares with the customeradd function.
        if request.form.get('Edit'):
            connection = getCursor()
            connection.execute("SELECT * FROM customers WHERE customer_id = %s ORDER BY familyname;", (int(customerId),))
            customerData = connection.fetchone()
            return render_template("enterdetails.html",customerid =customerId, customerdata= customerData)    
        else:
            # When the Report button is pressed, gets the values from the database and displays it on the customerhome page.
            # This is done so that the form and the results are on the same page and the user would not have to navigate away
            # in case a new report for a different customer needs to be generated. 
            connection = getCursor()
            #SQL get the customer data
            connection.execute("SELECT * FROM customers WHERE customer_id = %s ORDER BY familyname;", (int(customerId),))  
            customerData = connection.fetchone()
            #SQL get the customer list back when the form refreshes
            connection.execute("SELECT * FROM customers ORDER BY familyname;") #SQL to update the  new values 
            customerList = connection.fetchall()
            #SQL get the bookings of the selected customer 
            connection.execute("SELECT * FROM bookings WHERE customer = %s ORDER BY booking_date;", (int(customerId),))
            customerBookingData = connection.fetchall()
            #SQL get the total number of nights booked
            connection.execute("SELECT COUNT(booking_date) FROM bookings WHERE customer = %s;", (int(customerId),))
            totalNightsBooked = connection.fetchone()[0]
            #SQL get the average occupancy
            connection.execute("SELECT AVG(occupancy) FROM bookings WHERE customer = %s;", (int(customerId),))
            averageOccupancy = connection.fetchall()[0][0]
            return render_template("customerhome.html",customerid = customerId, customerdata = customerData, customerlist = customerList, customerbookingdata =customerBookingData, totalnightsbooked = totalNightsBooked,averageoccupancy = averageOccupancy)
        
@app.route("/customerhome/edit", methods=['POST'])
def customerhomeedit():
    # For this part the input values from the form are checked if they are valid
    customerId = request.form.get('customerid')
    firstName = request.form.get('firstname')
    familyName = request.form.get('familyname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    # Flags are added to send the result of the validation to the confirmation page       
    flagFirstName = is_valid_firstname(firstName)
    flagFamilyName = is_valid_familyname(familyName)
    flagEmail = is_valid_email(email)
    flagPhone = is_valid_phone(phone)
    # If they are all of them are valid they are written to the database, otherwise nothing is done.
    if (is_valid_firstname(firstName) and is_valid_familyname(familyName) and is_valid_email(email) and is_valid_phone(phone)):
        connection = getCursor()
        #SQL to update the  new values 
        connection.execute("UPDATE customers SET firstname = %s, familyname = %s, email = %s, phone = %s WHERE customer_id = %s;", (firstName, familyName, email, phone,customerId,))
    else:
        pass
    #Show the confirmation result
    return render_template("enterdetailsconfirmation.html",customerid =customerId, firstname=firstName,familyname=familyName, email = email, phone=phone, flagfirstname = flagFirstName, flagfamilyname = flagFamilyName, flagemail= flagEmail, flagphone =flagPhone)

@app.route("/customerhomeget/", methods=['GET','POST'] )
# This is just to get the correct argument to be passed to the customerhome 
def customerhomeget():
    return customerhome(request.args['customerid'])
