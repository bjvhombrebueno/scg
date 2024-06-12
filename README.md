# COMP636 Web App Assessment Report
### Ben Joseph Hombrebueno 1161713

### LIST CAMPERS
There are 2 ways to get to the view campers page, when it is first entered by 'GET' the user will be asked for the date, when entered by 'POST' it will list the campers for that date based on the form input. In datepickercamper.html the form and the results are on the same page so that it is easier for the user to search for another date without navigating to a different page every time.

### ADD BOOKING
There are 2 ways to get to the booking page, when it is first entered by 'GET' the user will be asked for the date, occupancy, and the number of nights, and when entered by 'POST' it will list the available sites and choose which customer to make the booking for.
Once those are submitted and validated, then it will proceed to the confirmation page. There are 3 templates used here the datepicker.html, the bookingform.html, and the bookingconfirmation.html
 
### CUSTOMER SEARCH
There are 2 ways to get into the customer search page, when 'GET' is used it displays the input box for the search string and by 'POST' it shows all the search results. In customersearch.html the form and the results are on the same page so that it is easier for the user to search for another date without navigating to a different page every time. Also, two buttons link to the booking page and the customer home page which passes the customer id automatically. This is done to make it easier to redirect to those pages without entering the customer's name again. There is also a workaround done to input a search string to the SQL string as there is no way to input it directly. It was done by splitting the string and placing the search string in between.

### CUSTOMER ADD and EDIT

The customer add and edit share the same function which is why they share the same input (enterdetails.html) and confirmation (enterdetails.html) templates . When entered by 'GET' it shows the form to get the inputs from the customer and when entered by 'POST' it shows the confirmation. It was decided to move the confirmation to a different page because of display issues when displaying the confirmation on the same page. The routes are different because for customer add an INSERT to the database is done while an UPDATE is done for edit. 

### CUSTOMER REPORT and EDIT
There are 2 ways to get into the customer home page, when 'GET' is used it displays the selection box for the customer and 2 buttons ('POST') for either editing or generating the report for the selected customer. Editing and viewing are grouped as they both need a customer ID to function. When the Report button is pressed, gets the values from the database and displays them on the customerhome page. This is done so that the form and the results are on the same page and the user would not have to navigate away in case a new report for a different customer needs to be generated. 

### Validation
For this page, there is a problem with the email validation. Email addresses not in the correct format are not caught in the automatic validation by Bootstrap even when setting the input type="email". Things like be@d get accepted. So for entering the details, everything is sent to the back end where the secondary validation is made. The pattern works for validating the text inputs and the phone number using the default browser validation, but they are checked again at the back end just the same. Flags are used to determine which inputs are invalid and need to be changed. 

### Bootstrap CSS
A navigation bar was added which automatically resizes when the browser window is changed. At its minimum, it changes to a small toggle dropdown menu. This is done to make the webpage more responsive to the user. The background was set to a dark template and most of the forms are rendered by Bootstrap. It was considered to use a sidebar but the app might be difficult to view on smaller screens. The interface used scales better when viewed at any width. 

### Database questions:
1.CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(45) NULL,
  `familyname` VARCHAR(60) NOT NULL,
  `email` VARCHAR(255) NULL,
  `phone` VARCHAR(12) NULL,
  PRIMARY KEY (`customer_id`));

2.CONSTRAINT `customer`
    FOREIGN KEY (`customer`)
    REFERENCES `scg`.`customers` (`customer_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION

3.
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P1', '5');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P4', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P2', '3');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P5', '8');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P3', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U1', '6');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U2', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U3', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U4', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U5', '2');

4. bookings table, 'timestamp' column, TIMESTAMP data format 

5. There should be a table let's say 'bookedby' that shows the booking and the customer ID of the person who did the booking or the staff. There should also be a way to record the time or a process to determine who would be able to book the site if multiple people were trying to book a site at the same time, to prevent double booking. 