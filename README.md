# Django 3 apps

This repo contains some major apps worth boasting about during my adventure as a Django developer.
The core folder consists of several ultra basic apps.

## hr_working_hours
The hr_working_hours app helps to track and calculate working hours of temporary contractors. Moreover, it enables to
draw reports about their activity and days off during their contract time. The working time can be adjusted and
 monitored buy workers' immediate supervisors. All records can be turned into reports that divide data into locations,
 managers, a particular worker and a selected company.

Working time records can be created manually by supervisors or can be transferred automatically from a card reader placed 
at the door. The reader (see software for it: https://github.com/andrzejzmuda/kivy_CardReader) scans the card number,
recognizes if a worker enters or leaves premises, and eventually saves it to a local database.
 After that, the record is transferred by airflow service
  (see software for it: https://github.com/andrzejzmuda/airflow_dags) to the hr_working_hours app database.


## canteen
The canteen app has been developed to ease the processs of orders managing in the company canteen. The main goal is to 
enable workers to place an order for a meal for a selected day, using several terminals placed in the premises.
 The order is then added to the database. Each day after 9.30 AM the reports with the orders for the particular day is 
 automatically sent to the caterer. The application allows to create an array of different reports useful for HR dept and
   accountancy dept.
