# API-Server---Tevel

# server.py 
API server for data menegment based SQL.

**class DatabaseManager:**  <br />
Responsible for the database file.  <br />
Creating a connection with the SQL file, creating a new table, inserting data, checking if a table exists. <br />

**class APIService:** <br />
The API endpoint functions. <br />
Endpoint for creating a new table and inserting data. <br />

# test.py 
An unit test for checking valid and invalid requests. <br />

# Built With
* flask
* sqlite3
* unittest
