import sqlite3


conn = sqlite3.connect('database/companies.db')
db = conn.cursor()


db.execute("CREATE TABLE IF NOT EXISTS 'Profiles' ('Email' varchar(100) PRIMARY KEY NOT NULL, 'Company Name' varchar(100) NOT NULL, 'Company Number' bigint NOT NULL, 'Company Address' varchar(10000) NOT NULL, 'password' text NOT NULL)")

