Running the Tornado Message Posting example app
====================================
This is a simple message posting app that uses MySQL to store posts(messages). Since it depends on MySQL, you need to set up either MySQL or Docker with MySQL image for the app to run.


1. Install prerequisites and build tornado version 5

   See http://www.tornadoweb.org/ for installation instructions. 

2. Install MySQL or Docker if needed

   Consult the documentation for your platform. Under OS X you
   can run “brew install mysql". Or you can download the MySQL 
   PKG file from http://dev.mysql.com/downloads/mysql/. 
   Alternatively, you can choose to use the official mysql docker 
   image from https://hub.docker.com/_/mysql/ or run “docker pull
   mysql” to get the latest mysql image.   

3. Install Python prerequisites (Default Python 3.6)

   Since the app uses python asyncio properties. Install the packages
   aiomysql, uvloop (e.g. using pip3). The app works at least later 
   than (including) Python version 3.5.

3. Connect to Docker (MySQL image) and create a database and user for the app.

   > docker run -p 3301:3306 --name some-mysql -e MYSQL_ROOT_PASSWORD=pw -d mysql:latest

   Connect to MySQL as a user that can create databases and users:
   > mysql -u root -h 127.0.0.1 -p -P 3301

   By default, the app uses the database named “mysql”. 

   View your databases:
   mysql> show databases;

4. Create the tables in your new database.

   The app will create a table named “msg_tb2” during the Tornado Web Application 
   component initialization.

   *Alternatively, you can use the provided schema.sql file by running this command:
   mysql --user=root —h 127.0.0.1 —p password=pw —P 3301 database=mysql < schema.sql

   Note each new test run of the app will erase the table and rebuild if succeeded.

5. Run the app 

   With the default user, password, and database you can just run:
   ./asyncEx.py
   You can also run from PyCharm. Please configure environment settings accordingly.


6. Visit your new app webpage

   Open http://localhost:8080/ in your web browser. Type the post in the submit window,
   the site will show all history posts sorted by posting order with post ids.


   
